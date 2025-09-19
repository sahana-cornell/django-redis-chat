import os
import json
import time
from typing import List, Dict, Tuple

import redis
from django.conf import settings

# --- Redis connection singleton ---
_redis = None

def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        host = os.environ.get("REDIS_HOST", "redis")
        port = int(os.environ.get("REDIS_PORT", "6379"))
        _redis = redis.from_url(os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/1"))
    return _redis

# --- Message storage helpers ---
def _msg_list_key(conv_id: int) -> str:
    return f"chat:{conv_id}:messages"

def _msg_seq_key(conv_id: int) -> str:
    return f"chat:{conv_id}:seq"

def list_messages(conv_id: int, limit: int = 50) -> List[Dict]:
    r = get_redis()
    # grab the last N messages
    raw = r.lrange(_msg_list_key(conv_id), -limit, -1)
    out: List[Dict] = []
    for s in raw:
        try:
            out.append(json.loads(s))
        except Exception:
            # ignore bad entries
            pass
    return out

def append_message(conv_id: int, *, user_id: int, text: str) -> Dict:
    """
    Append a message for conv_id and return the saved dict.
    """
    r = get_redis()
    msg_id = int(r.incr(_msg_seq_key(conv_id)))
    msg = {
        "id": msg_id,
        "user_id": int(user_id),
        "text": text,
        "ts": int(time.time()),
    }
    r.rpush(_msg_list_key(conv_id), json.dumps(msg))
    # optional: keep a rolling TTL on the list so stale rooms age out
    # comment this out if you want messages to stay forever in Redis
    r.expire(_msg_list_key(conv_id), 60 * 60 * 24 * 3)  # 3 days
    return msg

# --- WebSocket rate limit helper ---
def check_ws_rate_limit(user_id: int, conv_id: int) -> Tuple[bool, int]:
    """
    Fixed window: allow up to WS_RATE_COUNT per WS_RATE_WINDOW_SEC per (conv,user).
    Returns (allowed, retry_after_seconds).
    """
    r = get_redis()
    window = int(getattr(settings, "WS_RATE_WINDOW_SEC", 10))
    limit = int(getattr(settings, "WS_RATE_COUNT", 5))
    key = f"rate:ws:{conv_id}:{user_id}"

    # incr + read TTL in a pipeline for consistency
    pipe = r.pipeline()
    pipe.incr(key)
    pipe.ttl(key)
    count, ttl = pipe.execute()

    # First hit in window: set expiry
    if ttl == -1:
        r.expire(key, window)
        ttl = window

    allowed = count <= limit
    retry_after = max(ttl, 1) if not allowed else 0
    return allowed, retry_after
