from cachetools import TTLCache
from functools import lru_cache

# Basit future kullanım için placeholder
api_cache = TTLCache(maxsize=128, ttl=300)

@lru_cache(maxsize=64)
def memo_font(path: str, size: int):
    return (path, size)