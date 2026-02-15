from rest_framework.response import Response

def ratelimit_view(request, exception):
    return Response(
        {"detail": "Too many requests. Try again later."},
        status=429
    )