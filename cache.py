import redis
import json
import hashlib
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
r = redis.from_url(REDIS_URL, decode_responses=True)

TTL = 60 * 60 * 24 * 7  # 7 jours


def _key(name: str) -> str:
    clean = name.lower().strip()
    h     = hashlib.md5(clean.encode()).hexdigest()[:8]
    return f"casier:{clean.replace(' ', '_')}:{h}"


def get_cache(name: str) -> dict | None:
    try:
        data = r.get(_key(name))
        if data:
            print(f"[CACHE HIT] {name}")
            return json.loads(data)
        print(f"[CACHE MISS] {name}")
        return None
    except Exception as e:
        print(f"[CACHE ERROR] {e}")
        return None


def set_cache(name: str, data: dict) -> None:
    try:
        r.setex(_key(name), TTL, json.dumps(data, ensure_ascii=False))
        print(f"[CACHE SET] {name} — TTL {TTL}s")
    except Exception as e:
        print(f"[CACHE ERROR] {e}")
