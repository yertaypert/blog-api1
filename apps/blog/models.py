# Django modules
from django.db import models
from django.conf import settings
from django.utils import timezone



class Category(models.Model):

    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name
    name_en = models.CharField(max_length=100, default="")
    name_ru = models.CharField(max_length=100, default="")
    name_kk = models.CharField(max_length=100, default="")

    def get_name(self, language):

        if language == "ru":
            return self.name_ru
        elif language == "kk":
            return self.name_kk

        return self.name_en


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.name


class Post(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    body = models.TextField()

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True
    )

    tags = models.ManyToManyField(Tag, blank=True)

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"Comment by {self.author.email}"
