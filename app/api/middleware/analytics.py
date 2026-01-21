"""Analytics Middleware"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.database.models import Visitor, ApiUsage
from app.database.connection import get_db
import hashlib
from app.config import Settings
import time
import re

class AnalyticsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track page visits and API usage
    Runs on every request unless disabled
    """
    async def dispatch(self, request: Request, call_next):
        # Skip if analytics disabled
        if not Settings.ENABLES_ANALYTICS:
            return await call_next(request)
        
        # Track start time for reponse time
        start_time = time.time()

        # Process request
        response = await call_next(request)

        process_time_ms = (time.time() - start_time)*1000

        # Add response time header if enabled
        if Settings.TRACK_RESPONSE_TIME:
            response.headers["X-Process-Time"] = str(round(process_time_ms, 2))

        # Skip tracking for certain paths
        skip_path = ['/static', '/api/redoc', '/openapi.json', '/health', '/favicon.ico']
        if any(request.url.path.startswith(path) for path in skip_path):
            return response
        

        # Track asynchronously (don't block responses)
        try:
            await self._track_request(request, response, process_time_ms)
        except Exception as e:
            # Don't let analytics errors break the app
            print(f"Analytics tracking error: {e}")
        return response
    
    async def _track_request(self, request: Request, response, process_time_ms: float):
        """Track the request in database"""

        # Get Client info

        ip = request.client.host if request.client else "unknown"
        ip_hash = hashlib.sha256(ip.encode()).hexdigest()
        user_agent = request.headers.get('user-agent', '')
        referrer = request.headers.get('referer', '')

        # Detect deveice type from user agent
        device_type = self._detect_device(user_agent)

        # Determine if this is a page view or API call
        is_api = request.url.path.startswith('/api/')

        with get_db() as db:
            if is_api:
                # Track API usage
                api_usage = ApiUsage(
                    endpoint = request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    response_time_ms=process_time_ms,
                    ip_hash=ip_hash,
                    error_message=None if response.stattus_code < 400 else "Error occurred"
                )
                db.add(api_usage)

            else:
                visitor = Visitor(
                    page=request.url.path,
                    ip_hash=ip_hash,
                    user_agent=user_agent[:500],
                    referrer=referrer[:500],
                    device_type=device_type,
                    browser=self._detect_os(user_agent)
                )
                db.add(visitor)

    def _detect_device(self, user_agent: str) -> str:
        """Detect device type from user agent"""
        ua_lower = user_agent.lower()

        # Mobile devices
        mobile_keywords = ['mobile', 'android', 'iphone', 'ipod', 'blackberry', 'windows phone']
        if any(keyword in ua_lower for keyword in mobile_keywords):
            return 'mobile'
        
        # Tablet
        tablet_keywords = ['ipad', 'tablet', 'kindle']
        if any(keyword in ua_lower for keyword in tablet_keywords):
            return 'tablet'
        
        # Default to desktop

        return "desktop"
    
    def _detect_browser(self, user_agent: str) -> str:
        """Detect browwser from user agent"""

        ua_lower = user_agent.lower()

        if 'edge' in ua_lower or 'edg/' in ua_lower:
            return 'Edge'
        elif 'chrome' in ua_lower and 'safari' in ua_lower:
            return 'Chrome'
        elif 'firefox' in ua_lower:
            return 'Firefox'
        
        elif 'safari' in ua_lower and 'chrome' not in ua_lower:
            return 'Safari'
        
        elif 'opera' in ua_lower or 'opr/' in ua_lower:
            return 'Opera'
        
        elif 'msie' in ua_lower or 'trident/' in ua_lower:
            return 'Internet Explorer'
        
        return 'Unknown'
    
    def _detect_os(self, user_agent: str) -> str:
        """Detect operating system from user agent"""

        ua_lower = user_agent.lower()

        if 'windows' in ua_lower:
            return 'Windows'
        elif 'mac os' in ua_lower or 'macos' in ua_lower:
            return 'macOS'
        elif 'linux' in ua_lower:
            return 'Linux'
        elif 'android' in ua_lower:
            return 'Android'
        elif 'iphone' in ua_lower or 'ipad' in ua_lower or 'ipod' in ua_lower:
            return 'iOS'
        
        return 'Unknown'
