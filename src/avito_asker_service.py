import logging
from typing import Dict, Any
from src.deps.common_avito_utils.redis_wrapper.redis_wrapper import Redis

class AvitoAskerService:
    
    def __init__(self, app_conf: Dict[str, Any], redis: Redis, logger: logging.Logger):
        self.redis = redis
        self.logger = logger

    async def start_service(self):
        pass