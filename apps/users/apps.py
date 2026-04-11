# Django modules
from django.apps import AppConfig


class UsersConfig(AppConfig):
    defaul_auto_field = "django.db.models.BigAutoField"
    name = 'apps.users'
