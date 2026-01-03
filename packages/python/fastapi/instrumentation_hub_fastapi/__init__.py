"""Public exports for the Instrumentation Hub FastAPI adapter."""

from .bootstrap import FastAPIInstrumentation, InstrumentationResult, setup_fastapi_instrumentation
from .config import Config, ConfigModel
from .observability.otel_collector.metrics.middleware import MetricsMiddleware
from .utils.rate_limit import rate_limited_log

__all__ = [
	"FastAPIInstrumentation",
	"InstrumentationResult",
	"Config",
	"ConfigModel",
	"MetricsMiddleware",
	"rate_limited_log",
	"setup_fastapi_instrumentation",
]
