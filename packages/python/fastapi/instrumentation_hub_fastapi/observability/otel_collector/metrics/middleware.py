"""Custom FastAPI middleware shipped with Instrumentation Hub."""
from __future__ import annotations

import time

from opentelemetry.metrics import Meter
from starlette.middleware.base import BaseHTTPMiddleware


class MetricsMiddleware(BaseHTTPMiddleware):
    """Collect request counts and durations for every HTTP request."""

    def __init__(self, app, meter: Meter):
        super().__init__(app)
        self.meter = meter
        self._init_instruments()

    def _init_instruments(self) -> None:
        self.request_counter = self.meter.create_counter(
            name="http_server_requests_total",
            description="Total HTTP requests",
            unit="1",
        )
        self.duration_histogram = self.meter.create_histogram(
            name="http_request_duration_seconds",
            description="HTTP request duration in seconds",
            unit="s",
        )

    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        attributes = {
            "method": request.method,
            "path": request.url.path,
            "status_code": str(response.status_code),
        }
        self.request_counter.add(1, attributes)
        self.duration_histogram.record(duration, attributes)
        return response
