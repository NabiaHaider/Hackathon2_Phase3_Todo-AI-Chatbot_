from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp
from collections import defaultdict
import time
from typing import Dict, Any

class InMemoryRateLimiterMiddleware(BaseHTTPMiddleware):
    # Limits for /api/v1/chat endpoint
    # user_id -> {"last_access_time": float, "request_count": int}
    chat_request_tracker: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {"last_access_time": 0.0, "request_count": 0}
    )
    RATE_LIMIT_SECONDS = 60 # 1 minute window
    RATE_LIMIT_REQUESTS = 30 # 30 requests per minute

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/v1/chat"):
            # In a real app, user_id would come from JWT, for now use IP
            # For simplicity, using client IP as a temporary identifier
            # The actual user_id propagation will come later (T011)
            user_identifier = request.client.host if request.client else "unknown"

            current_time = time.time()
            user_data = self.chat_request_tracker[user_identifier]

            # Reset count if window has passed
            if current_time - user_data["last_access_time"] > self.RATE_LIMIT_SECONDS:
                user_data["request_count"] = 0
                user_data["last_access_time"] = current_time

            # Check if limit exceeded
            if user_data["request_count"] >= self.RATE_LIMIT_REQUESTS:
                retry_after = int(self.RATE_LIMIT_SECONDS - (current_time - user_data["last_access_time"]))
                response = JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded. Try again later."},
                )
                response.headers["Retry-After"] = str(max(0, retry_after))
                response.headers["X-RateLimit-Limit"] = str(self.RATE_LIMIT_REQUESTS)
                response.headers["X-RateLimit-Remaining"] = "0"
                return response
            
            user_data["request_count"] += 1
            user_data["last_access_time"] = current_time # Update last access time for each request within window

            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(self.RATE_LIMIT_REQUESTS)
            response.headers["X-RateLimit-Remaining"] = str(max(0, self.RATE_LIMIT_REQUESTS - user_data["request_count"]))
            return response
        else:
            return await call_next(request)
