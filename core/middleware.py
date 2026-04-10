import logging


logger = logging.getLogger('debug_requests')


class DebugRequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.debug(
            'Incoming request: %s %s from %s',
            request.method,
            request.get_full_path(),
            request.META.get('REMOTE_ADDR', '-'),
        )
        return self.get_response(request)
