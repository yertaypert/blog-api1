# Django + Third Party modules
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Project modules
from .models import Notification


def send_new_comment_to_websocket(comment):
    """
    Broadcast a new comment to all websocket clients connected to the same post
    """
    channel_layer = get_channel_layer()

    message = {
        "comment_id": comment.id,
        "author": {
            "id": comment.author.id,
            "email": comment.author.email,
        },
        "body": comment.body,
        "created_at": comment.created_at.isoformat(),
    }

    async_to_sync(channel_layer.group_send)(
        f"post_comments_{comment.post.slug}",
        {
            "type": "comment.message",
            "message": message,
        }
    )


def publish_post(post):
    channel_layer = get_channel_layer()

    data = {
        "post_id": post.id,
        "title": post.title,
        "slug": post.slug,
        "author": {
            "id": post.author.id,
            "email": post.author.email,
        },
        "published_at": post.created_at.isoformat(),
    }

    async_to_sync(channel_layer.group_send)(
        "posts_stream",
        {
            "type": "post_published",
            "message": data,
        }
    )


def create_comment_notification(comment):
    """
    Create a notification only for the post author
    """
    if comment.author_id == comment.post.author_id:
        return
    
    Notification.objects.create(
        recipient=comment.post.author,
        comment=comment,
    )


def notify_new_comment(comment): # NOTE: can be removed
    """
    Call this after any comment created
    Triggers WebSocket + Notification
    """
    send_new_comment_to_websocket(comment)
    