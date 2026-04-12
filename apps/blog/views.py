# Python modules
import logging
from typing import Any

# Django modules
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

# Django Rest Framework modules
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

# Project modules
from .models import Comment, Post
from .permissions import IsOwnerOrReadOnly
from .redis import publish_comment_event
from .serializers import CommentSerializer, PostCreateUpdateSerializer, PostSerializer
from apps.notifications.utils import send_new_comment_to_websocket, publish_post, notify_new_comment
from .tasks import invalidate_posts_list_cache
from apps.notifications.tasks import process_new_comment


LOGGER_NAME = "blog"
POSTS_CACHE_KEY_PREFIX = "published_posts_list"
POSTS_CACHE_KEY_REGISTRY = f"{POSTS_CACHE_KEY_PREFIX}:keys"
COMMENTS_ACTION = "comments"

logger = logging.getLogger(LOGGER_NAME)


class PostPagination(PageNumberPagination):
    page_size = 10


class PostViewSet(viewsets.ViewSet):
    lookup_field = "slug"
    pagination_class = PostPagination
    CACHE_KEY_PREFIX = POSTS_CACHE_KEY_PREFIX
    CACHE_KEY_REGISTRY = POSTS_CACHE_KEY_REGISTRY

    def get_permissions(self) -> list[BasePermission]:
        if self.action in ("create", "partial_update", "destroy", COMMENTS_ACTION):
            if self.action == COMMENTS_ACTION and self.request.method == "GET":
                permission_classes = [permissions.AllowAny]
            elif self.action == COMMENTS_ACTION:
                permission_classes = [permissions.IsAuthenticated]
            else:
                permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.action in ("list", "retrieve", COMMENTS_ACTION):
            return Post.objects.filter(status=Post.Status.PUBLISHED).select_related(
                "author", "category"
            ).prefetch_related("tags")
        return Post.objects.all().select_related("author", "category").prefetch_related("tags")

    def get_object(self) -> Post:
        queryset = self.get_queryset()
        post = get_object_or_404(queryset, slug=self.kwargs[self.lookup_field])
        self.check_object_permissions(self.request, post)
        return post

    def get_serializer_class(self) -> type[serializers.Serializer]:
        if self.action in ("create", "partial_update"):
            return PostCreateUpdateSerializer
        return PostSerializer

    @extend_schema(
        summary="List published posts",
        description="Returns a paginated list of published posts. Results are cached for 60 seconds. Supports language localization via 'Accept-Language' header.",
        tags=["Posts"],
        parameters=[
            OpenApiParameter("page", type=int, description="Page number for pagination")
        ],
        responses={200: PostSerializer(many=True)}
    )
    def list(self, request: Request) -> Response:
        queryset = self.get_queryset().order_by("-created_at")
        page_number = request.query_params.get("page", "1")
        cache_key = f"{self.CACHE_KEY_PREFIX}:{page_number}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = self.get_serializer_class()(page, many=True)
        response = paginator.get_paginated_response(serializer.data)
        cache.set(cache_key, response.data, timeout=60)
        self.track_posts_cache_key(cache_key)
        return response

    @extend_schema(
        summary="Retrieve a post",
        description="Returns detailed information about a single published post by its slug.",
        tags=["Posts"],
        responses={
            200: PostSerializer,
            404: OpenApiExample("Not Found", value={"detail": "Not found."}),
        }
    )
    def retrieve(self, request: Request, slug: str | None = None) -> Response:
        post = self.get_object()
        serializer = self.get_serializer_class()(post)
        return Response(serializer.data)

    @extend_schema(
        summary="Create a new post",
        description="Creates a new post. Requires authentication. Invalidator Celery task is triggered to clear the posts list cache. If published, triggers a WebSocket broadcast.",
        tags=["Posts"],
        request=PostCreateUpdateSerializer,
        responses={
            201: PostSerializer,
            400: OpenApiExample("Validation Error", value={"title": ["This field is required."]}),
            401: OpenApiExample("Unauthorized", value={"detail": "Authentication credentials were not provided."}),
        }
    )
    @method_decorator(ratelimit(key="user", rate="20/m", method="POST", block=True))
    def create(self, request: Request) -> Response:
        try:
            serializer = self.get_serializer_class()(data=request.data)
            serializer.is_valid(raise_exception=True)
            post = serializer.save(author=request.user)
            invalidate_posts_list_cache.delay()
            if post.status == "published":
                publish_post(post)
        except serializers.ValidationError:
            logger.warning("Post creation failed for user: %s", request.user)
            raise
        except APIException:
            raise
        except Exception:
            logger.exception("Unexpected error during post creation for user: %s", request.user)
            raise

        logger.info("Post created: %s by %s", post.slug, request.user.email)
        self.invalidate_posts_list_cache()
        response_serializer = PostSerializer(post)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Update a post",
        description="Partially updates an existing post. Only the author can perform this action. Clears the posts list cache and may trigger a WebSocket broadcast if status changes to published.",
        tags=["Posts"],
        request=PostCreateUpdateSerializer,
        responses={
            200: PostSerializer,
            403: OpenApiExample("Forbidden", value={"detail": "You do not have permission to perform this action."}),
            404: OpenApiExample("Not Found", value={"detail": "Not found."}),
        }
    )
    def partial_update(self, request: Request, slug: str | None = None) -> Response:
        try:
            post = self.get_object_for_write(slug)
            serializer = self.get_serializer_class()(post, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            post = serializer.save()
            invalidate_posts_list_cache.delay()
            if post.status == "published":
                publish_post(post)
        except serializers.ValidationError:
            logger.warning("Post update failed for slug %s by %s", slug, request.user)
            raise
        except APIException:
            raise
        except Exception:
            logger.exception("Unexpected error during post update for slug %s by %s", slug, request.user)
            raise

        logger.info("Post updated: %s by %s", post.slug, request.user.email)
        self.invalidate_posts_list_cache()
        return Response(PostSerializer(post).data)

    @extend_schema(
        summary="Delete a post",
        description="Deletes a post by its slug. Only the author can perform this action. Clears the posts list cache.",
        tags=["Posts"],
        responses={
            204: None,
            403: OpenApiExample("Forbidden", value={"detail": "You do not have permission to perform this action."}),
            404: OpenApiExample("Not Found", value={"detail": "Not found."}),
        }
    )
    def destroy(self, request: Request, slug: str | None = None) -> Response:
        try:
            post = self.get_object_for_write(slug)
            logger.info("Post deleted: %s by %s", post.slug, request.user.email)
            post.delete()
            invalidate_posts_list_cache.delay()
        except APIException:
            raise
        except Exception:
            logger.exception("Unexpected error during post deletion for slug %s by %s", slug, request.user)
            raise

        self.invalidate_posts_list_cache()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object_for_write(self, slug: str | None) -> Post:
        post = get_object_or_404(
            Post.objects.all().select_related("author", "category").prefetch_related("tags"),
            slug=slug,
        )
        self.check_object_permissions(self.request, post)
        return post

    @extend_schema(
        summary="Manage post comments",
        description="GET: List all comments for a post. POST: Add a new comment to a post. Creating a comment triggers a Celery task for processing and sends a notification.",
        tags=["Comments"],
        responses={
            200: CommentSerializer(many=True),
            201: CommentSerializer,
            401: OpenApiExample("Unauthorized", value={"detail": "Authentication credentials were not provided."}),
        }
    )
    @action(detail=True, methods=["get", "post"], url_path="comments", url_name="comments")
    def comments(self, request: Request, slug: str | None = None) -> Response:
        post = self.get_object()

        if request.method == "GET":
            comments = Comment.objects.filter(post=post).select_related("author").order_by("created_at")
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

        try:
            serializer = CommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            comment = serializer.save(author=request.user, post=post)
            self.publish_comment_created(post, comment, request.user.email)
            process_new_comment.delay(comment.id)
            # send_new_comment_to_websocket(comment)
            notify_new_comment(comment)
        except serializers.ValidationError:
            logger.warning("Comment creation failed for post %s by %s", post.slug, request.user)
            raise
        except APIException:
            raise
        except Exception:
            logger.exception("Unexpected error during comment creation for post %s by %s", post.slug, request.user)
            raise

        logger.info("Comment added to post %s by %s", post.slug, request.user.email)
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    def track_posts_cache_key(self, cache_key: str) -> None:
        cached_keys = cache.get(self.CACHE_KEY_REGISTRY, set())
        if cache_key in cached_keys:
            return
        cache.set(self.CACHE_KEY_REGISTRY, cached_keys | {cache_key}, timeout=60)

    def invalidate_posts_list_cache(self) -> None:
        cached_keys = cache.get(self.CACHE_KEY_REGISTRY, set())
        if cached_keys:
            cache.delete_many(list(cached_keys))
        cache.delete(self.CACHE_KEY_REGISTRY)

    def publish_comment_created(self, post: Post, comment: Comment, author_email: str) -> None:
        event: dict[str, Any] = {
            "type": "comment_created",
            "post_slug": post.slug,
            "author": author_email,
            "body": comment.body,
        }
        try:
            publish_comment_event(event)
        except Exception:
            logger.exception("Failed to publish comment_created event for %s", post.slug)


class CommentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_permissions(self) -> list[BasePermission]:
        return [permission() for permission in self.permission_classes]

    def get_object(self) -> Comment:
        comment = get_object_or_404(Comment.objects.select_related("author", "post"), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, comment)
        return comment

    @extend_schema(
        summary="Update a comment",
        description="Updates an existing comment. Only the author can perform this action.",
        tags=["Comments"],
        responses={
            200: CommentSerializer,
            403: OpenApiExample("Forbidden", value={"detail": "You do not have permission to perform this action."}),
        }
    )
    def partial_update(self, request: Request, pk: int | None = None) -> Response:
        try:
            comment = self.get_object()
            serializer = CommentSerializer(comment, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            comment = serializer.save()
        except serializers.ValidationError:
            logger.warning("Comment update failed for comment %s by %s", pk, request.user)
            raise
        except APIException:
            raise
        except Exception:
            logger.exception("Unexpected error during comment update for comment %s by %s", pk, request.user)
            raise

        return Response(CommentSerializer(comment).data)
    
    @extend_schema(
        summary="Delete a comment",
        description="Deletes a comment. Only the author or a moderator can perform this action.",
        tags=["Comments"],
        responses={
            204: None,
            403: OpenApiExample("Forbidden", value={"detail": "You do not have permission to perform this action."}),
        }
    )
    def destroy(self, request: Request, pk: int | None = None) -> Response:
        try:
            comment = self.get_object()
            comment.delete()
        except APIException:
            raise
        except Exception:
            logger.exception("Unexpected error during comment deletion for comment %s by %s", pk, request.user)
            raise

        return Response(status=status.HTTP_204_NO_CONTENT)
