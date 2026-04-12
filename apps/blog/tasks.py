from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from settings.base import AUTH_USER_MODEL
from datetime import timedelta
import redis
import json
import logging

from .models import Post, Comment
from settings.conf import REDIS_URL, POSTS_CACHE_KEY_REGISTRY


logger = logging.getLogger(__name__)
redis_client = redis.Redis.from_url(REDIS_URL)
User = AUTH_USER_MODEL
DAILY_STATS_LAST_HOURS = 24


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def invalidate_posts_list_cache():
    """
    Invalidate the posts list cache after create/update/delete

    Automatic retires are important for cache tasks becasue Redis can have transient
    connection drops or brief unavailablity during high load
    Retrying guarantess the cache is eventually cleared
    """
    cached_keys = cache.get(POSTS_CACHE_KEY_REGISTRY, set())
    if cached_keys:
        cache.delete_many(list(cached_keys))
    cache.delete(POSTS_CACHE_KEY_REGISTRY)


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def publish_scheduled_posts():
    """
    Find posts with status=scheduled and publish_at <= now(), set to published
    Trigger the SSE for each published post

    Automatic retries are important for scheduled post tasks because:
        - DB updates and Redis publish might fail during high load
        - Retrying guarantess post is published and SSE will be received
    """
    now = timezone.now()
    posts_to_publish = Post.object.filter(
        status=Post.Status.SCHEDULED,
        published_at=now
    ).select_related("author", "category")

    for post in posts_to_publish:
        post.status = Post.Status.PUBLISHED
        post.save(update_fields=["status"])

        try:
            event = {
                "type": "post_published",
                "post_slug": post.slug,
                "title": post.title,
                "published_at": post.created_at.isoformat(),
            }
            redis_client.publish("see_post_published", json.dumps(event))

        except Exception:
            logger.exception("Failed to publish SSE for scheduled post %s", post.slug)

        logger.info("Auto published scheduled post: %s", post.slug)
    

    invalidate_posts_list_cache.delay()


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def generate_daily_stats():
    """
    Log daily statistics for the last 24 hours

    Automatic retries are important here because:
        - Simple queries can fail because of db connection issues
        - Retrying ensures the daily log entry is not lost
    """
    since = timezone.now() - timedelta(DAILY_STATS_LAST_HOURS) # NOTE: tried to avoid magic nums
    new_posts = Post.objects.filter(created_at=since).count()
    new_comments = Comment.objects.filter(created_at=since).count()
    new_users = User.objects.filter(date_joined=since).count()

    logger.info("Daily Stats last %s hours: %s new posts | %s new comments | %s new users", 
                DAILY_STATS_LAST_HOURS,
                new_posts,
                new_comments,
                new_users
                )
