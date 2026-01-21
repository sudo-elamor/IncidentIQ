import time
import json
import redis
from datetime import datetime
from .definitions import queue_depth, queue_oldest_age

QUEUE_NAMES = ["api_queue", "agent_queue", "dlq"]

redis_client = redis.Redis(
    host="broker",
    port=6379,
    decode_responses=True,
)

def get_message_timestamp(raw):
    try:
        msg = json.loads(raw)
        return msg.get("timestamp")
    except Exception:
        return None

def collect():
    while True:
        for q in QUEUE_NAMES:
            depth = redis_client.llen(q)
            queue_depth.labels(queue=q).set(depth)

            if depth > 0:
                raw = redis_client.lindex(q, -1)
                ts = get_message_timestamp(raw)
                if ts:
                    age = time.time() - ts
                    queue_oldest_age.labels(queue=q).set(age)
                else:
                    queue_oldest_age.labels(queue=q).set(0)
            else:
                queue_oldest_age.labels(queue=q).set(0)

        time.sleep(5)
