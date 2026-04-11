# apps/core/exceptions.py
from typing import Any

from rest_framework.views import exception_handler
from rest_framework.response import Response
from django_ratelimit.exceptions import Ratelimited


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    if isinstance(exc, Ratelimited):
        return Response(
            {"detail": "Too many requests. Try again later."},
            status=429
        )

    return exception_handler(exc, context)
