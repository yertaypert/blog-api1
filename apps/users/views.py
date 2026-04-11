# Python modules
import logging
from typing import Any

# Django modules
from django.http import JsonResponse
from django.http import HttpRequest
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

# Django Rest Framework modules
from rest_framework import serializers, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

# Project modules
from apps.core.constants import RATE_LIMIT_EXCEEDED_DETAIL
from .constants import REGISTER_RATE_LIMIT, USERS_LOGGER_NAME
from .serializers import LoggingTokenObtainPairSerializer, RegisterSerializer


logger = logging.getLogger(USERS_LOGGER_NAME)


@method_decorator(ratelimit(key='ip', rate=REGISTER_RATE_LIMIT, method='POST', block=True), name='create')
class RegisterView(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
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


def ratelimit_response(request: HttpRequest, exception: Exception) -> JsonResponse:
    return JsonResponse(
        {'detail': RATE_LIMIT_EXCEEDED_DETAIL},
        status=429,
    )
