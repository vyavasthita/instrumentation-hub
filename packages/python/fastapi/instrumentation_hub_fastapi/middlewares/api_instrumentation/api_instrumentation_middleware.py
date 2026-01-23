# This file was missing. Restoring the middleware implementation for API instrumentation.
import time
import json
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from opentelemetry.metrics import get_meter
from .config import MetricType, InstrumentationConfigFactory, InstrumentationSanitizationConfig


class ApiInstrumentationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API observability: logs requests/responses, tracks metrics, and safely handles sensitive data.
    """
    def __init__(self, app, config: 'InstrumentationConfigFactory' = None, sanitization_config: 'InstrumentationSanitizationConfig' = None, service_name: str = "instrumentation_hub", log_level: str = "INFO"):
        super().__init__(app)
        meter = get_meter(__name__)

        config = config or InstrumentationConfigFactory()
        self.sanitization_config = sanitization_config or InstrumentationSanitizationConfig()

        self.metrics = self._create_metrics(meter, config)

        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(log_level.upper())

    def _create_metrics(self, meter, config):
        metrics = {}
        
        if MetricType.REQUEST_COUNT in config.enabled_metrics:
            metrics['request_count'] = meter.create_counter(
                "http_requests_total", description="Total HTTP requests"
            )

        if MetricType.REQUEST_LATENCY in config.enabled_metrics:
            metrics['request_latency'] = meter.create_histogram(
                "http_request_latency_seconds", description="HTTP request latency"
            )

        if MetricType.ERROR_COUNT in config.enabled_metrics:
            metrics['error_count'] = meter.create_counter(
                "http_request_errors_total", description="Total HTTP request errors"
            )

        return metrics

    def safe_truncate(self, data):
        if isinstance(data, dict):
            return {
                key: ("***" if key.lower() in self.sanitization_config.sensitive_fields else str(value)[:self.sanitization_config.max_field_length])
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self.safe_truncate(item) for item in data]
        elif isinstance(data, str):
            return data[:self.sanitization_config.max_field_length]
        else:
            return str(data)[:self.sanitization_config.max_field_length]

    async def _extract_request_info(self, request: Request):
        info = {
            "method": request.method,
            "url": str(request.url),
            "headers": self.safe_truncate(dict(request.headers)),
            "query_params": self.safe_truncate(dict(request.query_params)),
        }

        try:
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
        if 'request_count' in self.metrics:
            self.metrics['request_count'].add(1, {"method": request.method, "endpoint": request.url.path, "http_status": status_code})
        
        if 'request_latency' in self.metrics:
            self.metrics['request_latency'].record(process_time, {"endpoint": request.url.path})
        
        if 'error_count' in self.metrics and status_code >= 400:
            self.metrics['error_count'].add(1, {"endpoint": request.url.path, "http_status": status_code})

    async def _extract_response_json(self, response):
        try:
            response_body = b""

            async for chunk in response.body_iterator:
                response_body += chunk

            async def single_chunk():
                yield response_body
                
            response.body_iterator = single_chunk()
            response_content = response_body.decode()

            try:
                response_json = json.loads(response_content)
            except Exception:
                response_json = response_content
        except Exception:
            response_json = "<unparsable>"
        return response_json

    def _log_request_response(self, request_info, response_json, status_code, process_time):
        log_data = {
            "event": "request",
            "request": request_info,
            "response": self.safe_truncate(response_json),
            "status_code": status_code,
            "latency": process_time
        }
        self.logger.info(json.dumps(log_data))

    async def _get_response(self, request: Request, call_next, request_info):
        response = None
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            status_code = 500
            if 'error_count' in self.metrics:
                self.metrics['error_count'].add(1, {"endpoint": request.url.path, "http_status": status_code})
            self.logger.error(json.dumps({
                "event": "error",
                "request": request_info,
                "error": str(exc)
            }))
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"}), status_code
        
        return response, status_code

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_info = await self._extract_request_info(request)
        response, status_code = await self._get_response(request, call_next, request_info)

        process_time = time.time() - start_time

        self._record_metrics(request, status_code, process_time)

        response_json = await self._extract_response_json(response)

        self._log_request_response(request_info, response_json, status_code, process_time)
        
        return response