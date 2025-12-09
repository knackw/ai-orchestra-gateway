import uuid
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Context variable to hold request ID for logging access
request_id_context: ContextVar[str] = ContextVar("request_id", default="")

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
    1. Generates a unique Request ID for every request (or uses X-Request-ID header if trusted).
    2. Sets it in a ContextVar for logging.
    3. Adds it to request.state.
    4. Adds X-Request-ID header to response.
    """
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Generate ID (ignoring incoming header for security/consistency in this MVP, 
        # or we could trust internal LB headers if reliable)
        req_id = str(uuid.uuid4())
        
        # Set in context var (token allows resetting if needed, but for request scope it's fine)
        token = request_id_context.set(req_id)
        
        # Set in request state
        request.state.request_id = req_id
        
        try:
            response = await call_next(request)
            # Add header to response
            response.headers["X-Request-ID"] = req_id
            return response
        finally:
            # Clean up context var
            request_id_context.reset(token)

def get_request_id() -> str:
    """Helper to get current request ID from context."""
    return request_id_context.get()
