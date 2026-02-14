from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Post, Comment
from .serializers import PostSerializer, PostCreateUpdateSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly

import logging

logger = logging.getLogger('blog')


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    lookup_field = 'slug'

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

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        logger.info('Post created: %s by %s', post.slug, self.request.user.email)

    def perform_update(self, serializer):
        post = serializer.save()
        logger.info('Post updated: %s by %s', post.slug, self.request.user.email)

    def perform_destroy(self, instance):
        slug = instance.slug
        user_email = self.request.user.email
        instance.delete()
        logger.info('Post deleted: %s by %s', slug, user_email)
        

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
                return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
            serializer = CommentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
