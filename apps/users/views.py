# Python modules
import logging
from typing import Any

# Django modules
from django.http import HttpRequest, JsonResponse
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

# Django Rest Framework modules
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, OpenApiExample

# Project modules
from apps.core.constants import RATE_LIMIT_EXCEEDED_DETAIL
from .constants import REGISTER_RATE_LIMIT, USERS_LOGGER_NAME
from .serializers import (
    LoggingTokenObtainPairSerializer,
    RegisterSerializer,
    UserPreferencesSerializer,
)


logger = logging.getLogger(USERS_LOGGER_NAME)


@method_decorator(ratelimit(key="ip", rate=REGISTER_RATE_LIMIT, method="POST", block=True), name="create")
class RegisterView(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer

    @extend_schema(
        summary="Register a new user",
        description="Creates a new user account with email, password, and optional profile data. Rate-limited to prevent abuse. No side effects like emails (configured in settings).",
        tags=["Auth"],
        responses={
            201: RegisterSerializer,
            400: OpenApiExample("Validation Error", value={"email": ["This field is required."]}),
            429: OpenApiExample("Rate Limit Exceeded", value={"detail": RATE_LIMIT_EXCEEDED_DETAIL}),
        },
        examples=[
            OpenApiExample(
                "Successful Registration",
                value={
                    "email": "user@example.com",
                    "password": "strongpassword123",
                    "first_name": "John",
                    "last_name": "Doe"
                },
                request_only=True,
            )
        ]
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        email = request.data.get("email")
        logger.info("Registration attempt for email: %s", email)

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
        except serializers.ValidationError:
            logger.warning("Registration failed for email: %s", email)
            raise
        except Exception:
            logger.exception("Unexpected registration error for email: %s", email)
            raise

        logger.info("User registered: %s", user.email)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Update user preferences",
        description="Updates the authenticated user's preferred language and timezone. Language detection middleware uses these settings to localize responses.",
        tags=["Auth"],
        request=UserPreferencesSerializer,
        responses={
            200: UserPreferencesSerializer,
            401: OpenApiExample("Unauthorized", value={"detail": "Authentication credentials were not provided."}),
        },
        examples=[
            OpenApiExample(
                "Update Preferences",
                value={
                    "preferred_language": "ru",
                    "preferred_timezone": "Asia/Almaty"
                },
                request_only=True,
            )
        ]
    )
    @action(detail=False, methods=["patch"], permission_classes=[IsAuthenticated])
    def preferences(self, request: Request) -> Response:
        serializer = UserPreferencesSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@extend_schema(
    summary="Login and obtain JWT tokens",
    description="Authenticates a user and returns access and refresh JWT tokens. Rate-limited to prevent brute-force attacks.",
    tags=["Auth"],
    responses={
        200: LoggingTokenObtainPairSerializer,
        401: OpenApiExample("Invalid Credentials", value={"detail": "No active account found with the given credentials"}),
        429: OpenApiExample("Rate Limit Exceeded", value={"detail": RATE_LIMIT_EXCEEDED_DETAIL}),
    }
)
class LoginView(TokenObtainPairView):
    serializer_class = LoggingTokenObtainPairSerializer


def ratelimit_response(request: HttpRequest, exception: Exception) -> JsonResponse:
    return JsonResponse(
        {"detail": RATE_LIMIT_EXCEEDED_DETAIL},
        status=429,
    )
