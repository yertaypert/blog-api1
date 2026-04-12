from celery import shared_task

from apps.blog.models import Comment
from .utils import create_comment_notification, send_new_comment_to_websocket


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retires=3,
)
def process_new_comment(comment_id: int):
    """
    Handle the creation of comment:
        - Create notificaition
        - Publish websocket message

    Automatic retries are important for comment processing because:
        - DB writes or Redis publish might fail
        - Retrying ensures the user still gets the real time notification and count
    """
    comment = Comment.objects.select_related('post', 'author').get(pk=comment_id)

    create_comment_notification(comment)
    send_new_comment_to_websocket(comment)