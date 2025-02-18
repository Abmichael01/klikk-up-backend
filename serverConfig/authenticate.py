from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions
import logging

logger = logging.getLogger(__name__)

def enforce_csrf(request):
    """
    Enforce CSRF validation by checking CSRF token.
    """
    check = CSRFCheck(request)
    check.process_request(request)
    
    csrf_cookie = request.COOKIES.get("csrftoken")
    csrf_header = request.META.get("HTTP_X_CSRFTOKEN")
    
    # If CSRF token is in cookie but not in header, set it in the header
    if csrf_cookie and not csrf_header:
        request.META['HTTP_X_CSRFTOKEN'] = csrf_cookie

    reason = check.process_view(request, None, (), {})
    if reason:
        logger.error(f"CSRF Failed: {reason}")
        raise exceptions.PermissionDenied(f"CSRF Failed: {reason}")

class CustomAuthentication(JWTAuthentication):
    def authenticate(self, request):
        """
        Custom authentication that enforces CSRF protection for session-based JWT authentication.
        """
        header = self.get_header(request)
        raw_token = None

        if header:
            raw_token = self.get_raw_token(header)
        else:
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])

        if not raw_token:
            logger.warning("No JWT token found in headers or cookies.")
            return None

        validated_token = self.get_validated_token(raw_token)

        # Ensure CSRF check before using JWT authentication
        enforce_csrf(request)

        return self.get_user(validated_token), validated_token

