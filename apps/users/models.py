# Python modules
from typing import Any

# Django modules
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)
from django.utils import timezone


class UserManager(BaseUserManager):

    def create_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "User":
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email).lower()

        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        first_name: str,
        last_name: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "User":
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, first_name, last_name, password, **extra_fields)
    

class User(AbstractBaseUser, PermissionsMixin):
    class PreferredLanguage(models.TextChoices):
        ENGLISH = "en", "English"

    DEFAULT_LANGUAGE = PreferredLanguage.ENGLISH
    DEFAULT_TIMEZONE = settings.TIME_ZONE

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    preferred_language = models.CharField(
        max_length=2,
        choices=PreferredLanguage.choices,
        default=DEFAULT_LANGUAGE,
    )
    preferred_timezone = models.CharField(max_length=50, default=DEFAULT_TIMEZONE)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self) -> str:
        return self.email
