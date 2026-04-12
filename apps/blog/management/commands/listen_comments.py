# Python modules
import json
from typing import Any

# Django modules
from django.core.management.base import BaseCommand

# Project modules
from apps.blog.redis import COMMENTS_CHANNEL, get_redis_connection


class Command(BaseCommand):
    help = "Subscribe to the Redis comments channel and print incoming events."

    def handle(self, *args: Any, **options: Any) -> None:
        pubsub = get_redis_connection().pubsub()
        pubsub.subscribe(COMMENTS_CHANNEL)

        self.stdout.write(
            self.style.SUCCESS(f"Listening on '{COMMENTS_CHANNEL}' channel. Press Ctrl+C to stop.")
        )

        try:
            for message in pubsub.listen():
                if message.get("type") != "message":
                    continue

                payload = self.decode_payload(message.get("data"))
                self.stdout.write(payload)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Stopping listener."))
        finally:
            pubsub.close()


    def decode_payload(self, payload: Any) -> str:
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")

        if isinstance(payload, str):
            try:
                return json.dumps(json.loads(payload), ensure_ascii=True)
            except json.JSONDecodeError:
                return payload

        return json.dumps(payload, ensure_ascii=True)
