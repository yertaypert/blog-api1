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
from drf_spectacular.utils import extend_schema, OpenApiExample

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
    
    @extend_schema(
        summary="Get unread notifications count",
        description="Returns the total number of unread notifications for the authenticated user. Useful for periodic polling.",
        tags=["Notifications"],
        responses={
            200: OpenApiExample("Count Response", value={"unread_count": 5}),
            401: OpenApiExample("Unauthorized", value={"detail": "Authentication credentials were not provided."}),
        }
    )
    @action(detail=False, methods=["get"], url_path="count")
    def count(self, request):
        unread_count = self.get_queryset().filter(is_read=False).count()
        return Response({"unread_count": unread_count})
    
    @extend_schema(
        summary="List user notifications",
        description="Returns a paginated list of all notifications for the authenticated user.",
        tags=["Notifications"],
        responses={200: NotificationSerializer(many=True)}
    )
    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Mark all notifications as read",
        description="Updates all unread notifications for the authenticated user to read status.",
        tags=["Notifications"],
        responses={
            200: OpenApiExample("Success", value={"detail": "All notifications marked as read"}),
            401: OpenApiExample("Unauthorized", value={"detail": "Authentication credentials were not provided."}),
        }
    )
    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response(
            {"detail": "All notifications marked as read"},
              status=status.HTTP_200_OK,
        )


