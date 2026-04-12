from celery import shared_task
from django.core.cache import cache


POSTS_CACHE_KEY_REGISTRY = "posts_list_registry"


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