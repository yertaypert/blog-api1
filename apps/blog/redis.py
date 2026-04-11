# Python modules
import json
from typing import Any

# Django + Third Party modules
import redis
from django.conf import settings


COMMENTS_CHANNEL = "comments"


def get_redis_connection() -> redis.Redis:
    return redis.from_url(settings.REDIS_DJANGORLAR_URL)


def publish_comment_event(event: dict[str, Any]) -> int:
    return get_redis_connection().publish(COMMENTS_CHANNEL, json.dumps(event))
