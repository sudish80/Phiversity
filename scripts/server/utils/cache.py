import os
import redis
import json
from typing import Any
from ..logger import logger

class CacheService:
    def __init__(self):
        self.url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        try:
            self.client = redis.from_url(self.url, decode_responses=True)
            self.client.ping()
            self.enabled = True
        except Exception as e:
            logger.warning(f"Redis not available: {e}. Caching disabled.")
            self.enabled = False

    def get(self, key: str):
        if not self.enabled: return None
        data = self.client.get(key)
        return json.loads(data) if data else None

    def set(self, key: str, value: Any, expire: int = 3600):
        if not self.enabled: return
        self.client.set(key, json.dumps(value), ex=expire)

cache = CacheService()
