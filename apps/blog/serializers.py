# Django modules
from django.conf import settings

# Django Rest Framework modules
from rest_framework import serializers

# Project modules
from .models import Category, Tag, Post, Comment


User = settings.AUTH_USER_MODEL


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


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

    class Meta:
        model = Post
        fields = [
            "id", "title", "slug", "body", "author_email",
            "category", "tags", "status", "created_at", "updated_at"
        ]


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["title", "slug", "body", "category", "tags", "status"]
