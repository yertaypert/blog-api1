# Python modules
import logging

# Django + Third Party modules
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

# Project modules
from apps.blog.models import Comment
from .models import Notification
from .utils import create_comment_notification, send_new_comment_to_websocket


logger = logging.getLogger(__name__)
NOTIFICATIONS_EXPIRY_DAYS = 30


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


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retires=3,
)
def clear_expired_notifications():
    """
    Delete notifications older that 30 days

    Automatic retries are important for cleaning up tasks:
        - Large delete operations may lock or cause DB issues
        - Retrying ensures old notifications are removed
    """
    since = timezone.now() - timedelta(NOTIFICATIONS_EXPIRY_DAYS) # NOTE: tried to avoid magic nums
    deleted_count = Notification.objects.filter(created_at=since).delete()

    logger.info("Removed %s expired notifications for last %s days:", deleted_count, NOTIFICATIONS_EXPIRY_DAYS)