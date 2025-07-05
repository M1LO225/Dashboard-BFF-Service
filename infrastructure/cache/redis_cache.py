import redis
import json
import logging
from typing import Optional

from core.config import settings
from domain.entities.dashboard import DashboardData

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self):
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB
            )
            self.client.ping()
            logger.info("Redis cache connected successfully.")
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None

    def get(self, key: str) -> Optional[DashboardData]:
        if not self.client:
            return None
        
        cached_data = self.client.get(key)
        if cached_data:
            logger.info(f"Cache HIT for key: {key}")
            data_dict = json.loads(cached_data)
            return DashboardData(**data_dict)
        
        logger.info(f"Cache MISS for key: {key}")
        return None

    def set(self, key: str, value: DashboardData):
        if not self.client:
            return
        
        self.client.setex(
            key,
            settings.CACHE_EXPIRATION_SECONDS,
            value.model_dump_json()
        )
        logger.info(f"Cache SET for key: {key}")