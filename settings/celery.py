# Python modules
import os

# Third part modules
from celery import Celery
from celery.schedules import crontab

# Project modules
from settings.conf import ENV_ID


os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"settings.env.{ENV_ID}")


app = Celery("blog")


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# # Common interval launch with Celery
app.conf.beat_schedule = {
    "spam-everyone-every-minute": {
        "task": "apps.blog.tasks.publish_scheduled_posts",
        "schedule": 60,
    },
    "clear_expired_notifications": {
        "task": "apps.notifications.tasks.clear_expired_notifications",
        "schedule": crontab(hour=3, minute=0),
    },
    "generate_daily_stats": {
        "task": "apps.blog.tasks.generate_daily_stats",
        "schedule": crontab(hour=0, minute=0),
    },
}