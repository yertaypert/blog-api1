from django.apps import AppConfig


class BlogConfig(AppConfig):
    defaul_auto_field = "django.db.models.BigAutoField"
    name = 'apps.blog'
