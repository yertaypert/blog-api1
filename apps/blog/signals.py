from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings
from .models import Post

@receiver([post_save, post_delete], sender=Post)
def clear_post_cache(sender, instance, **kwargs):
    """
    Whenever a Post is saved or deleted, clear the language-specific caches.
    """
    # The 'base' key defined in ViewSet
    base_key = "published_posts_list"
    
    for lang_code, _ in settings.LANGUAGES:
        cache.delete(f"{base_key}:{lang_code}")