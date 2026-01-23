import time
import json
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from opentelemetry.metrics import get_meter


SENSITIVE_FIELDS = {'password', 'token', 'secret', 'authorization'}
MAX_FIELD_LENGTH = 128


class ApiInstrumentationMiddleware(BaseHTTPMiddleware):
    """
        Middleware for API observability: logs requests/responses, tracks metrics, and safely handles sensitive data.
    """
    def __init__(self, app):
        """
        Initialize the middleware, set up metrics counters/histograms and logger.

        Args:
            app: FastAPI app instance
        """
        super().__init__(app)

        meter = get_meter(__name__)
        self.request_count = meter.create_counter(
            "http_requests_total", description="Total HTTP requests"
        )
        self.request_latency = meter.create_histogram(
            "http_request_latency_seconds", description="HTTP request latency"
        )
        self.error_count = meter.create_counter(
            "http_request_errors_total", description="Total HTTP request errors"
        )
        self.logger = logging.getLogger("instrumentation_hub")
        self.logger.setLevel(logging.INFO)

    @classmethod
    def safe_truncate(cls, data):
        """
        Truncate sensitive or long fields in a dict, list, or string for safe logging.
        Sensitive fields are masked with '***'.

        Args:
            data: dict, list, str, or any JSON-serializable type

        Returns:
            Truncated/masked version of the input data

        Example:
            >>> ApiInstrumentationMiddleware.safe_truncate({'password': 'secret', 'username': 'bob'})
            {'password': '***', 'username': 'bob'}
            >>> ApiInstrumentationMiddleware.safe_truncate(['a'*200, 'b'])
            ['aaaaaaaa... (truncated)', 'b']
        """
        # Handle dict: mask sensitive fields and truncate values
        if isinstance(data, dict):
            return {
                key: ("***" if key.lower() in SENSITIVE_FIELDS else str(value)[:MAX_FIELD_LENGTH])
                for key, value in data.items()
            }
        # Handle list: recursively truncate each item
        elif isinstance(data, list):
            return [cls.safe_truncate(item) for item in data]
        # Handle string: truncate
        elif isinstance(data, str):
            return data[:MAX_FIELD_LENGTH]
        # Fallback: convert to string and truncate
        else:
            return str(data)[:MAX_FIELD_LENGTH]
    
    async def _extract_request_info(self, request: Request):
        """
        Extract and sanitize request information for logging.

        Args:
            request: FastAPI Request object

        Returns:
            dict with method, url, headers, query_params, and body (all truncated/masked)

        Example:
            info = await self._extract_request_info(request)
        """
        # Collect method, url, headers, and query params
        info = {
            "method": request.method,
            "url": str(request.url),
            "headers": self.safe_truncate(dict(request.headers)),
            "query_params": self.safe_truncate(dict(request.query_params)),
        }

        try:
            # Read and parse body if present
            body = await request.body()
            if body:
                parsed = json.loads(body.decode())
                info["body"] = self.safe_truncate(parsed)
            else:
                info["body"] = {}
        except Exception:
            info["body"] = "<unparsable>"

        return info
    
    def _record_metrics(self, request: Request, status_code: int, process_time: float):
        """
        Record metrics for the request: count, latency, and errors.

        Args:
            request: FastAPI Request
            status_code: HTTP status code
            process_time: request latency in seconds

        Example:
            self._record_metrics(request, 200, 0.123)
        """
        self.request_count.add(1, {"method": request.method, "endpoint": request.url.path, "http_status": status_code})
        self.request_latency.record(process_time, {"endpoint": request.url.path})

        if status_code >= 400:
            self.error_count.add(1, {"endpoint": request.url.path, "http_status": status_code})

    async def _extract_response_json(self, response):
        """
        Extract and parse the response body as JSON (if possible).

        Args:
            response: FastAPI Response object

        Returns:
            Parsed response JSON, string, or '<unparsable>'

        Example:
            resp_json = await self._extract_response_json(response)
        """
        try:
            response_body = b""

            # Read all chunks from the response body iterator
            async for chunk in response.body_iterator:
                response_body += chunk

            response.body_iterator = iter([response_body])
            response_content = response_body.decode()

            try:
                response_json = json.loads(response_content)
            except Exception:
                response_json = response_content

        except Exception:
            response_json = "<unparsable>"

        return response_json
    
    def _log_request_response(self, request_info, response_json, status_code, process_time):
        """
        Log the structured request and response data as a JSON log entry.

        Args:
            request_info: dict of request info
            response_json: parsed response body
            status_code: HTTP status code
            process_time: request latency in seconds

        Example:
            self._log_request_response(request_info, response_json, 200, 0.1)
        """
        log_data = {
            "event": "request",
            "request": request_info,
            "response": self.safe_truncate(response_json),
            "status_code": status_code,
            "latency": process_time
        }
        self.logger.info(json.dumps(log_data))

    async def _get_response(self, request: Request, call_next, request_info):
        """
        Call the next handler and catch exceptions, logging errors and returning a 500 if needed.

        Args:
            request: FastAPI Request
            call_next: function to call the next middleware/handler
            request_info: dict of request info for logging

        Returns:
            (response, status_code)

        Example:
            response, status = await self._get_response(request, call_next, request_info)
        """
        response = None
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code

        except Exception as exc:
            status_code = 500
            self.error_count.add(1, {"endpoint": request.url.path, "http_status": status_code})

            self.logger.error(json.dumps({
                "event": "error",
                "request": request_info,
                "error": str(exc)
            }))

            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"}), status_code
        
        return response, status_code
    
    async def dispatch(self, request: Request, call_next):
        """
        Main middleware entrypoint: logs, instruments, and returns the response.

        Args:
            request: FastAPI Request
            call_next: function to call the next middleware/handler

        Returns:
            Response object

        Example:
            # This is called automatically by FastAPI
        """
        start_time = time.time()  # Start timer for latency
        request_info = await self._extract_request_info(request)  # Extract request info

        response, status_code = await self._get_response(request, call_next, request_info)  # Get response

        process_time = time.time() - start_time  # Calculate latency
        self._record_metrics(request, status_code, process_time)  # Record metrics

        response_json = await self._extract_response_json(response)  # Extract response body

        self._log_request_response(request_info, response_json, status_code, process_time)  # Log everything
        return response
