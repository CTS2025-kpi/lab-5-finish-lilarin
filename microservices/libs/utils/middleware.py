import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from microservices.libs.utils.logger import trace_id_var


class TraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())
        trace_id_var.set(trace_id)

        response = await call_next(request)

        response.headers["X-Trace-ID"] = trace_id
        return response
