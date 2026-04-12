# Django + Third Party modules
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



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
