from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

from .models import Post, Comment
from .serializers import PostSerializer, PostCreateUpdateSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly

import redis
import json
import logging




logger = logging.getLogger('blog')
redis_client = redis.Redis(host='127.0.0.1', port=6379, db=2)


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Posts:
    - List & retrieve published posts (anyone)
    - Create, update, delete posts (authenticated)
    - Nested comments endpoint
    - Redis cache per language
    - Localized date formatting
    """

    queryset = Post.objects.all()
    lookup_field = 'slug'
    # This key MUST match the one used in signals.py
    CACHE_KEY = "published_posts_list"

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.AllowAny]
        return [p() for p in permission_classes]

    def get_queryset(self):
        if self.action in ['list', 'retrieve']:
            return Post.objects.filter(status=Post.Status.PUBLISHED)
        return Post.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostSerializer

    @extend_schema(
        summary="Create a new post",
        description="""
        Creates a post authored by the authenticated user.
        Cache for posts list is invalidated after creation.
        """,
        request=PostCreateUpdateSerializer,
        responses={
            201: PostSerializer,
            400: OpenApiResponse(description="Validation errors"),
            401: OpenApiResponse(description="Authentication required"),
        },
        examples=[
            OpenApiExample(
                "Request Example",
                value={
                    "title": "My New Post",
                    "slug": "my-new-post",
                    "body": "Some content",
                    "category": 1,
                    "tags": [1, 2],
                    "status": "PUBLISHED"
                },
                request_only=True
            ),
            OpenApiExample(
                "Response Example",
                value={
                    "id": 2,
                    "title": "My New Post",
                    "slug": "my-new-post",
                    "body": "Some content",
                    "author_email": "user@example.com",
                    "category": {"id": 1, "name": "Новости", "slug": "news"},
                    "tags": [{"id": 1, "name": "Django", "slug": "django"}],
                    "status": "PUBLISHED",
                    "created_at": "2026-03-14T14:00:00+05:00",
                    "updated_at": "2026-03-14T14:00:00+05:00"
                },
                response_only=True
            )
        ],
        tags=["Posts"]
    )
    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        logger.info('Post created: %s by %s', post.slug, self.request.user.email)
        

    @extend_schema(
        summary="Update a post",
        description="Updates a post authored by the authenticated user. Cache is invalidated.",
        request=PostCreateUpdateSerializer,
        responses={
            200: PostSerializer,
            400: OpenApiResponse(description="Validation errors"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Permission denied"),
        },
        tags=["Posts"]
    )
    def perform_update(self, serializer):
        post = serializer.save()
        logger.info('Post updated: %s by %s', post.slug, self.request.user.email)
        

    @extend_schema(
        summary="Delete a post",
        description="Deletes a post authored by the authenticated user. Cache is invalidated.",
        responses={
            204: OpenApiResponse(description="Post deleted"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Permission denied"),
        },
        tags=["Posts"]
    )
    def perform_destroy(self, instance):
        slug = instance.slug
        user_email = self.request.user.email
        instance.delete()
        logger.info('Post deleted: %s by %s', slug, user_email)
        

    @extend_schema(
        summary="List published posts",
        description="""
        Returns a list of published posts. Anonymous users see posts in UTC; authenticated users get dates localized to their timezone.
        Responses are cached per language in Redis. Cache is invalidated when posts are created, updated, or deleted.
        """,
        responses={
            200: PostSerializer(many=True),
        },
        examples=[
            OpenApiExample(
                "Response Example",
                value=[{
                    "id": 1,
                    "title": "My First Post",
                    "slug": "my-first-post",
                    "body": "Content...",
                    "author_email": "user@example.com",
                    "category": {"id": 1, "name": "Новости", "slug": "news"},
                    "tags": [{"id": 1, "name": "Django", "slug": "django"}],
                    "status": "PUBLISHED",
                    "created_at": "2026-03-14T12:00:00+05:00",
                    "updated_at": "2026-03-14T13:00:00+05:00"
                }],
                response_only=True
            )
        ],
        tags=["Posts"]
    )
    def list(self, request: Request, *args, **kwargs):

        language = get_language()
        cache_key = f"{self.CACHE_KEY}:{language}"

        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)

        cache.set(cache_key, response.data, timeout=60)

        return response
        


    @extend_schema(
        summary="List or add comments to a post",
        description="""
        GET: Returns all comments for the post.
        POST: Adds a new comment authored by the authenticated user.
        Redis event is published on creation. Validation ensures non-empty body.
        """,
        request=CommentSerializer,
        responses={
            200: CommentSerializer(many=True),
            201: CommentSerializer,
            400: OpenApiResponse(description="Comment body cannot be empty"),
            401: OpenApiResponse(description="Authentication required"),
        },
        examples=[
            OpenApiExample(
                "POST Request Example",
                value={"body": "Nice post!"},
                request_only=True
            ),
            OpenApiExample(
                "POST Response Example",
                value={
                    "id": 1,
                    "author_email": "user@example.com",
                    "body": "Nice post!",
                    "created_at": "2026-03-14T15:00:00+05:00"
                },
                response_only=True
            )
        ],
        tags=["Comments"]
    )
    @method_decorator(ratelimit(key='user', rate='20/m', method='POST', block=True))

    # Nested comments as an @action
    @action(detail=True, methods=['get', 'post'], url_path='comments', url_name='comments')
    def comments(self, request, slug=None):
        post = self.get_object()

        if request.method == 'GET':
            comments = Comment.objects.filter(post=post)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            if not request.user.is_authenticated:
                return Response({"detail": _("Authentication required.")}, status=status.HTTP_401_UNAUTHORIZED)
            
            if not request.data.get("body"):
                return Response(
                    {"detail": _("Comment body cannot be empty.")},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = CommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            comment = serializer.save(author=request.user, post=post)

            
            event = {
                "type": "comment_created",
                "post_slug": post.slug,
                "author": request.user.email,
                "body": comment.body,
            }

            redis_client.publish("comments", json.dumps(event))

            logger.info('Comment added to post %s by %s', post.slug, request.user.email)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
