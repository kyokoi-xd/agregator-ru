import time
from typing import Any, Dict, Optional
from .config import CACHE_TTL


class InMemoryCache:
    def __init__(self):
        self._store: Dict[str, Dict] = {}

    def get(self, key: str) -> Optional[Any]:
        rec = self._store.get(key)
        if not rec:
            return None
        if time.time() > rec['expires_at']:
            self._store.pop(key, None)
            return None
        return rec['value']
    
    def set(self, key: str, value: Any, ttl: int = CACHE_TTL) -> None:
        self._store[key] = {"value": value, "expires_at": time.time() + ttl}
