"""Security Headers Middleware"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses
    Helps protect against common web vulnerabilities
    """
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

         # Strict-Transport-Security (HSTS) - only in production with HTTPS
        # Uncomment when deploying with HTTPS
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content-Security-Policy - customize based on your needs
        # This is a basic policy, adjust for your requirements
        # response.headers["Content-Security-Policy"] = (
        #     "default-src 'self'; "
        #     "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
        #     "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        #     "font-src 'self' https://fonts.gstatic.com; "
        #     "img-src 'self' data: https:; "
        # )
        
        # Permissions-Policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=()"
        )
        
        return response
