import logging
from time import time

log = logging.getLogger("api.calls")

class APILoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        t0 = time()
        response = self.get_response(request)
        dt_ms = int((time() - t0) * 1000)
        user = getattr(request, "user", None)
        user_str = getattr(user, "id", None) or "-"
        log.info(
            f"{request.method} {request.path} -> {response.status_code} {dt_ms}ms user={user_str}"
        )
        return response
