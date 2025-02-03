import asyncio
import os
import logging
from src.deps.common_avito_utils.logger import get_logger
from src.avito_asker_service import AvitoAskerService
from src.deps.common_avito_utils.redis_wrapper import redis_wrapper
from src.deps.common_avito_utils.avito import AVITO_TO_AUTORESPONSE_SERVICE_CHANNEL_NAME
from typing import Dict, Any
from dotenv import load_dotenv

def config_field_secure(field: str):
    return False

async def main(app_conf: Dict[str, Any], logger: logging.Logger):
    redis = redis_wrapper.Redis(app_conf["redis_host"], app_conf["redis_port"], [AVITO_TO_AUTORESPONSE_SERVICE_CHANNEL_NAME], logger=logger)
    asker_service = AvitoAskerService(app_conf=app_conf, redis=redis, logger=logger)
    await asker_service.start_service()

    while True:
        await asyncio.sleep(0)

if __name__ == "__main__":
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    app_config = {
        "redis_host": os.environ.get("redis_host"),
        "redis_port": os.environ.get("redis_port"),
        "asking_form_url": os.environ.get("asking_form_url")
    }

    logger = get_logger("AVTIO AUTO RESPONSE", filename="avito_autoresponse.log")
    logger.info("Application config:\n%s", 
             '\n'.join([key + " : " + str(app_config[key])
                         for key in app_config if not config_field_secure(key)]))

    asyncio.run(main(app_conf=app_config, logger=logger))
