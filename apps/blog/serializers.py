# Django modules
from django.conf import settings
from django.utils import formats
from django.utils import timezone
from django.utils.translation import get_language

# Django Rest Framework modules
from rest_framework import serializers

# Project modules
from .models import Category, Tag, Post, Comment



User = settings.AUTH_USER_MODEL


class CategorySerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug"]

    def get_name(self, obj):
        lang = get_language()
        return obj.get_name(lang)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class CommentSerializer(serializers.ModelSerializer):
    author_email = serializers.ReadOnlyField(source='author.email')

    class Meta:
        model = Comment
        fields = ["id", "author_email", "body", "created_at"]


class PostSerializer(serializers.ModelSerializer):

    author_email = serializers.ReadOnlyField(source='author.email')
    tags = TagSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    created_at_local = serializers.SerializerMethodField()
    updated_at_local = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id", "title", "slug", "body", "author_email",
            "category", "tags", "status", "created_at", "updated_at"
        ]

    def get_created_at_local(self, obj):
        return formats.date_format(
            timezone.localtime(obj.created_at),
            "DATETIME_FORMAT"
        )

    def get_updated_at_local(self, obj):
        return formats.date_format(
            timezone.localtime(obj.updated_at),
            "DATETIME_FORMAT"
        )


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["title", "slug", "body", "category", "tags", "status"]
