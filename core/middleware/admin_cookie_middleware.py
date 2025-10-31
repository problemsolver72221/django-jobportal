# core/middleware/admin_cookie_middleware.py
from django.conf import settings


class AdminSessionCookieMiddleware:
    """
    Switches between admin and client cookies so their sessions are isolated.
    Keeps both admin and frontend login states independent.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Backup original cookie settings
        original_name = settings.SESSION_COOKIE_NAME
        original_path = getattr(settings, "SESSION_COOKIE_PATH", "/")
        original_csrf_name = getattr(settings, "CSRF_COOKIE_NAME", "csrftoken")

        # Use admin-specific cookies if path starts with /admin/
        if request.path.startswith("/admin/"):
            settings.SESSION_COOKIE_NAME = "admin_sessionid"
            settings.SESSION_COOKIE_PATH = "/admin/"
            settings.CSRF_COOKIE_NAME = "admin_csrftoken"
        else:
            settings.SESSION_COOKIE_NAME = "client_sessionid"
            settings.SESSION_COOKIE_PATH = "/"
            settings.CSRF_COOKIE_NAME = "client_csrftoken"

        # Process request/response
        response = self.get_response(request)

        # Restore global settings for the next request
        settings.SESSION_COOKIE_NAME = original_name
        settings.SESSION_COOKIE_PATH = original_path
        settings.CSRF_COOKIE_NAME = original_csrf_name

        return response
