from django.shortcuts import render
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import activate

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

from .serializers import RegisterSerializer
from .serializers import UserPreferencesSerializer
import logging


logger = logging.getLogger('users')


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='create')
class RegisterView(viewsets.GenericViewSet):
    """
    Handles user registration and preferences update.
    """
    
    serializer_class = RegisterSerializer

    @extend_schema(
        summary="Update user preferences",
        description="""
        Updates authenticated user's preferences: preferred language and timezone.
        Side effects: none.
        Authentication required.
        Request body must include valid timezone and language codes.
        """,
        request=UserPreferencesSerializer,
        responses={
            200: UserPreferencesSerializer,
            400: OpenApiResponse(description="Invalid timezone or language code"),
            401: OpenApiResponse(description="Authentication required")
        },
        examples=[
            OpenApiExample(
                "Request Example",
                value={
                    "preferred_language": "kk",
                    "timezone": "Asia/Almaty"
                },
                request_only=True
            ),
            OpenApiExample(
                "Response Example",
                value={
                    "preferred_language": "kk",
                    "timezone": "Asia/Almaty"
                },
                response_only=True
            )
        ],
        tags=["Auth"]
    )
    @action(detail=False, methods=["patch"], permission_classes=[IsAuthenticated])
    def preferences(self, request):

        serializer = UserPreferencesSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    @extend_schema(
        summary="Register a new user",
        description="""
        Creates a new user account with email, first name, last name, password, avatar.
        Sends a welcome email in the user's preferred language.
        Rate-limited: 5 requests per minute per IP.
        Side effects: sends welcome email, logs creation.
        Language/timezone: the welcome email is rendered in user's selected language.
        """,
        request=RegisterSerializer,
        responses={
            201: RegisterSerializer,
            400: OpenApiResponse(description="Validation errors (password mismatch, invalid timezone, etc.)"),
            429: OpenApiResponse(description="Too many requests"),
        },
        examples=[
            OpenApiExample(
                "Request Example",
                value={
                    "email": "user@example.com",
                    "first_name": "Ivan",
                    "last_name": "Petrov",
                    "password": "secret123",
                    "password2": "secret123",
                    "avatar": None,
                    "preferred_language": "ru",
                    "timezone": "Europe/Moscow"
                },
                request_only=True
            ),
            OpenApiExample(
                "Response Example",
                value={
                    "id": 1,
                    "email": "user@example.com",
                    "first_name": "Ivan",
                    "last_name": "Petrov",
                    "tokens": {
                        "refresh": "xxx",
                        "access": "yyy"
                    }
                },
                response_only=True
            )
        ],
        tags=["Auth"]
    )
    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        logger.info('Registration attempt for email: %s', email)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Activate user's language
        activate(user.preferred_language)

        template_name = f"emails/welcome_email_{user.preferred_language}.txt"

        message = render_to_string(template_name, {"user": user})

        send_mail(
            subject="Welcome to the Blog",
            message=message,
            from_email=None,
            recipient_list=[user.email],
        )

        logger.info('User registered: %s', user.email)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    
def ratelimit_response(request, exception):
    return Response(
        {"detail": _("Too many requests. Try again later.")},
        status=429
    )