# Python modules
from urllib.parse import parse_qs
import json
import logging

# Django + Third Party modules
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

# Django Rest Framework modules
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

# Project modules
from apps.blog.models import Post


LOGGER_NAME = "notification"

logger = logging.getLogger(LOGGER_NAME)


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WEBSOCKET CONNECT HIT")
        self.slug = self.scope["url_route"]["kwargs"]["slug"]
        self.room_group_name = f"post_comments_{self.slug}"

        try:
            self.post = await sync_to_async(Post.objects.get)(slug=self.slug)
        except Post.DoesNotExist:
            await self.close(code=4004)
            return
                
        query_string = self.scope["query_string"].decode()
        token_param = parse_qs(query_string)

        token = token_param.get('token', [None])[0]

        if not token:
            await self.close(code=4001)
            return
        
        
        try:
            AccessToken(token)
        except (InvalidToken, TokenError):
            await self.close(code=4001)
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def comment_message(self, event):
        # print("EVENT RECEIVED:", event)
        logger.info("EVENT RECEIVED: %s", event)
        await self.send(text_data=json.dumps(event["message"]))
