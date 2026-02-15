# apps/blog/management/commands/listen_comments.py
import json
import redis
from django.core.management.base import BaseCommand
# from django.conf import settings

class Command(BaseCommand):
    help = 'Listens to the Redis comments channel'

    def handle(self, *args, **options):
        r = redis.from_url('redis://127.0.0.1:6379/1')
        pubsub = r.pubsub()
        pubsub.subscribe('comments')

        self.stdout.write(self.style.SUCCESS('Listening for comments... Press Ctrl+C to stop.'))

        try:
            for message in pubsub.listen():
                if message['type'] == 'message':
                    # Decode bytes to string, then load JSON
                    data = json.loads(message['data'].decode('utf-8'))
                    self.stdout.write(
                        f"New Comment on [{data['post_slug']}]: "
                        f"'{data['body']}' by {data['author']}"
                    )
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nStopping listener...'))