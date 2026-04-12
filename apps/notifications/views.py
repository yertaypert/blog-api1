# Django + Third Party modules
import asyncio
import json
from channels.layers import get_channel_layer
from django.shortcuts import render
from django.http.response import StreamingHttpResponse

# Django Rest Framework modules
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Notification
from .serializers import NotificationSerializer
from apps.blog.views import PostPagination


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

class NotificationViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    pagination_class = PostPagination
    queryset = Notification.objects.all()

    def get_queryset(self):
        """
        Only return notifications for the current user
        """
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related("comment", "comment_author", "comment_post")
    
    @action(detail=False, methods=["get"], url_path="count")
    def count(self, request):
        """
        Polling endpoint for unread notification count

        HTTP Polling: 
            - Simplicity: easy to implement on the client
            - No persistent connection
            - Latency: updates are visible only on next poll
            - Server load: every active user makes a request every N seconds, more DB load

        Polling is acceptable when:
            - Notification are not so critical
            - Not too much number of users
            - Quick reliable fallback needed

        Switch to WebSockets or SSE when:
            - Need true real time (fast speeds)
            - High concurrency, need to reduce polling load
        """
        unread_count = self.get_queryset().filter(is_read=False).count()
        return Response({"unread_count": unread_count})
    

    def list(self, request):
        """
        Paginated list of all notifications for the current user
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

    def mark_all_read(self, request):
        """
        Mark all the notications for the current user as read
        """
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response(
            {"detail": "All notifications marked as read"},
              status=status.HTTP_200_OK,
        )


