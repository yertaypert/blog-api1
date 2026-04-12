# Django Rest Framework modules
from rest_framework.routers import DefaultRouter

# Project modules
from .views import CommentViewSet, PostViewSet
from apps.notifications.views import NotificationViewSet


router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = router.urls
