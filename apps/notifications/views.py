# Django + Third Party modules
import asyncio
import json
from channels.layers import get_channel_layer
from django.shortcuts import render
from django.http.response import StreamingHttpResponse


async def post_stream(request):
    """
    SSE: server -> client communication
    Works over HTTP
    For broadcasting feeds

    WebSockets is better to use if you need communication for both directions (eg. chat)
    """
    channel_layer = get_channel_layer()

    channel_name = await channel_layer.new_channel()

    await channel_layer.group_add("posts_stream", channel_name)

    async def event_generator():
        try:
            while True:
                message = channel_layer.receive(channel_name)

                data = message["data"]

                yield f"data: {json.dumps(data)}\n\n"
        except asyncio.CancelledError:
            channel_layer.group_discard("posts_stream", channel_name)

    return StreamingHttpResponse(
        event_generator(),
        content_type="text/event-stream"
    )