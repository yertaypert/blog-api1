# Python modules
from typing import Any

# Django + Third Party modules
from django_ratelimit.exceptions import Ratelimited

# Django Rest Framework modules
from rest_framework.views import exception_handler
from rest_framework.response import Response

# Project modules
from apps.core.constants import RATE_LIMIT_EXCEEDED_DETAIL


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    if isinstance(exc, Ratelimited):
        return Response(
            {"detail": RATE_LIMIT_EXCEEDED_DETAIL},
            status=429
        )

    return exception_handler(exc, context)
