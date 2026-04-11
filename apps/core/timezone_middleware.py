from django.utils import timezone
import pytz


class UserTimezoneMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:
            tzname = getattr(request.user, "preferred_timezone", "UTC")
        else:
            tzname = "UTC"

        try:
            timezone.activate(pytz.timezone(tzname))
        except Exception:
            timezone.activate(pytz.UTC)

        response = self.get_response(request)

        timezone.deactivate()

        return response