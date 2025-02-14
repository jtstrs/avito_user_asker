import logging
import asyncio
import json
from pymongo import AsyncMongoClient
from typing import Any
from src.deps.common_avito_utils.redis_wrapper.redis_wrapper import Redis
from src.deps.common_avito_utils.avito import AVITO_TO_TELEGRAM_CHANNEL_NAME, TELEGRAM_TO_AVITO_CHANNEL_NAME
from src.deps.common_avito_utils.avito import AVITO_AUTORESPONSE_DATABASE_NAME, AVITO_LEADS_COLLECTION_NAME, AVITO_ASKING_FORM_COLLECTION_NAME
from src.deps.common_avito_utils.avito_data_models import LeadModel

class AvitoAskerService:
    async def connect_to_mongo(self, mongo_client: AsyncMongoClient) -> bool:
        await mongo_client.aconnect()

        if not AVITO_AUTORESPONSE_DATABASE_NAME in await mongo_client.list_database_names():
            raise RuntimeError("Can't start service. Database is absent")

        database = mongo_client[AVITO_AUTORESPONSE_DATABASE_NAME]
        collections = await database.list_collection_names()

        if not AVITO_LEADS_COLLECTION_NAME in collections:
            raise RuntimeError("Can't start service. Peers collection is absent")

        if not AVITO_ASKING_FORM_COLLECTION_NAME in collections:
            raise RuntimeError("Can't start service. Asking form collection is absent")

        self.logger.info("Mongo database is valid")
        self.database = database
        self.collections = collections

    def __init__(self, redis: Redis, mongo: AsyncMongoClient, logger: logging.Logger):
        self.redis = redis
        self.mongo = mongo
        self.logger = logger

        self.redis.register_listening_cancelled_callback(lambda exception: self.on_redis_listen_cancelled(exception))
        self.redis.register_message_received_callback(lambda message: self.on_message_received_callback(message))

    async def init_asking_form(self):
        asking_form_response = await self.database[AVITO_ASKING_FORM_COLLECTION_NAME].find_one()
        if not asking_form_response:
            raise RuntimeError("Couldnt retrieve asking form")
        self.asking_form = asking_form_response["questions"]
        self.questions_count = asking_form_response["questions_count"]

        self.logger.info("Asking form:\n %s", str(self.asking_form))

    async def start_service(self):
        await self.connect_to_mongo(self.mongo)
        await self.init_asking_form()
        self.message_listen_task = asyncio.create_task(self.redis.listen())

    async def register_new_user(self, avito_id: int, chat_id: str):
        lead = LeadModel(avito_id=avito_id, ads_id=chat_id, autoask_state=0, meta=[])
        oid = await self.database[AVITO_LEADS_COLLECTION_NAME].insert_one(lead.model_dump())
        self.logger.debug("Register new lead with oid %s", oid)
        return lead

    async def ask_next_question(self):
        pass

    async def handle_incoming_message(self, message: dict[str, Any]):
        message_data = json.loads(message["data"])
        sender_id = message_data["sender"]
        user_id = message_data["received"]
        avito_chat = message_data["chat_id"]

        lead_data = await self.database[AVITO_LEADS_COLLECTION_NAME].find_one({"avito_id": sender_id})

        if not lead_data:
            lead = await self.register_new_user(avito_id=sender_id, chat_id=avito_chat)
        else:
            lead = LeadModel.model_validate(lead_data)
        await self.redis.get_connection().post_to_channel(channel=AVITO_TO_TELEGRAM_CHANNEL_NAME, message=message["data"])

        # autoask_finished = lead["autoask_state"] == self.questions_count
        # if autoask_finished:
        #     await self.redis.get_connection().post_to_channel(channel=AVITO_TO_TELEGRAM_CHANNEL_NAME, message=message_data)
        #     return
        
        # autoask_started = lead["autoask_state"] == 0
        # if autoask_started:
        #     await self.redis.get_connection().post_to_channel(channel=TELEGRAM_TO_AVITO_CHANNEL_NAME, message=)
        #     return

        # await self.ask_next_question()

    def handle_message_task_cancelling(self, task):
        if task.exception():
            self.logger.error("Error happened during handling message. Reason: %s", str(task.exception()))

    def on_message_received_callback(self, message: dict[str, Any]):
        message_task = asyncio.create_task(self.handle_incoming_message(message=message))
        message_task.add_done_callback(lambda task: self.handle_message_task_cancelling(task))

    def on_redis_listen_cancelled(self, exception: RuntimeError):
        if not exception:
            self.logger.info("Stop listening gracefully")
        self.logger.warning("Listening interrupted with an exception %s. Trying to restart", str(exception))
        self.message_listen_task = asyncio.create_task(self.redis.listen())