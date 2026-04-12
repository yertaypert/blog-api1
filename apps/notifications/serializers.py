# Django Rest Framework modules
from rest_framework import serializers

# Project modules
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    comment_id = serializers.IntegerField(source="comment_id", read_only=True)
    comment_body = serializers.CharField(source="comment.body", read_only=True)
    comment_author_email = serializers.EmailField(source="comment.author.email", read_only=True)
    post_slug = serializers.CharField(source="comment.post.slug", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "is_read",
            "created_at",
            "comment_id",
            "comment_body",
            "comment_author_email",
            "post_slug",
        ]