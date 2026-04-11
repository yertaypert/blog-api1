# Django Rest Framework modules
from rest_framework.routers import DefaultRouter

# Project modules
from .views import CommentViewSet, PostViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = router.urls
