import logging
import asyncio
import json
from typing import Any
from src.deps.common_avito_utils.redis_wrapper.redis_wrapper import Redis
from src.deps.common_avito_utils.avito import AVITO_TO_TELEGRAM_CHANNEL_NAME

class AvitoAskerService:
    message_listen_task: None

    def __init__(self, app_conf: dict[str, Any], redis: Redis, logger: logging.Logger):
        self.redis = redis
        self.logger = logger

        self.redis.register_listening_cancelled_callback(lambda exception: self.on_redis_listen_cancelled(exception))
        self.redis.register_message_received_callback(lambda message: self.on_message_received_callback(message))

    async def start_service(self):
        self.message_listen_task = asyncio.create_task(self.redis.listen())

    def on_message_received_callback(self, message: dict[str, Any]):
        self.logger.info("Receive new message %s. Post it to telegram without handling", message)
        message["data"] = str(message["data"])
        message["channel"] = str(message["channel"])

        serialized_message = json.dumps(message)
        asyncio.create_task(self.redis.get_connection().post_to_channel(channel=AVITO_TO_TELEGRAM_CHANNEL_NAME, message=str(serialized_message)))

    def on_redis_listen_cancelled(self, exception: RuntimeError):
        if not exception:
            self.logger.info("Stop listening gracefully")
        self.logger.warning("Listening interrupted with an exception %s. Trying to restart", str(exception))
        self.message_listen_task = asyncio.create_task(self.redis.listen())