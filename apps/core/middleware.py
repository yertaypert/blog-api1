from django.utils import translation
from django.conf import settings


class LanguageDetectionMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        language = None

        # user profile
        if request.user.is_authenticated:
            language = getattr(request.user, "preferred_language", None)

        # query parameter
        if not language:
            language = request.GET.get("lang")

        # Accept-Language header
        if not language:
            language = request.headers.get("Accept-Language")

        # fallback
        supported = dict(settings.LANGUAGES).keys()
        if language not in supported:
            language = settings.LANGUAGE_CODE

        translation.activate(language)
        request.LANGUAGE_CODE = language

        response = self.get_response(request)

        translation.deactivate()

        return response