# apps/core/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from django_ratelimit.exceptions import Ratelimited

def custom_exception_handler(exc, context):
    if isinstance(exc, Ratelimited):
        return Response(
            {"detail": "Too many requests. Try again later."},
            status=429
        )

    return exception_handler(exc, context)