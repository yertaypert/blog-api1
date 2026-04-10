import logging

from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework import serializers, status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import LoggingTokenObtainPairSerializer, RegisterSerializer


logger = logging.getLogger('users')


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='create')
class RegisterView(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        logger.info('Registration attempt for email: %s', email)

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
        except serializers.ValidationError:
            logger.warning('Registration failed for email: %s', email)
            raise
        except Exception:
            logger.exception('Unexpected registration error for email: %s', email)
            raise

        logger.info('User registered: %s', user.email)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = LoggingTokenObtainPairSerializer


def ratelimit_response(request, exception):
    return Response(
        {'detail': 'Too many requests. Try again later.'},
        status=429,
    )
