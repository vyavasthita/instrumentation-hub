
"""Entrypoints for wiring Instrumentation Hub into FastAPI."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional

from fastapi import FastAPI

from .config import Config
from .observability.otel_collector.logging.setup import OpenTelemetryLoggingSetup
from .observability.otel_collector.metrics.middleware import MetricsMiddleware
from .observability.otel_collector.metrics.setup import OpenTelemetryMetricsSetup
from .observability.otel_collector.tracing.setup import OpenTelemetryTracingSetup
from .enums.log_level import LogLevel


@dataclass
class InstrumentationResult:
    """Container returned after orchestration completes.

    Attributes:
        meter: The shared `Meter` instance for emitting custom metrics.
        logging_components: Struct that contains the OTLP logger provider + processor.
        tracer_provider: The configured tracer provider registered with OpenTelemetry.
    """

    meter: Any
    logging_components: Any
    tracer_provider: Any



class FastAPIInstrumentation:
    """
    High-level orchestration of logging, tracing, and metrics for FastAPI.

    Now accepts primitive parameters for configuration, not a ConfigModel object.

    Example:
        ```python
        from fastapi import FastAPI
        from instrumentation_hub_fastapi import FastAPIInstrumentation

        app = FastAPI()
        instrumentation = FastAPIInstrumentation(
            otlp_endpoint="http://localhost:4317",
            service_name="my-fastapi-service",
            log_level="INFO"
        )
        instrumentation.setup(app)
        ```
    """

    def __init__(
        self,
        otlp_endpoint: Optional[str] = None,
        service_name: Optional[str] = None,
        log_level: LogLevel | str = LogLevel.INFO,
        **kwargs
    ):
        """
        Accepts primitive configuration parameters for OpenTelemetry setup.
        - otlp_endpoint: The OTLP collector endpoint URL.
        - service_name: The logical service name for traces/metrics/logs.
        - log_level: Logging level (LogLevel enum or string, default INFO).
        - kwargs: Any additional config values supported by ConfigModel.
        """
        self.config = Config(
            otlp_endpoint=otlp_endpoint,
            service_name=service_name,
            log_level=log_level.value,
            **kwargs
        )

    def setup(self, app: FastAPI) -> InstrumentationResult:
        """
        Attach logging, tracing, metrics, and middleware to the provided FastAPI app.
        Returns an InstrumentationResult with meter, logging, and tracing objects.
        """
        # Set up OpenTelemetry logging
        logging_components = OpenTelemetryLoggingSetup(self.config).setup_logging()

        # Set up OpenTelemetry tracing
        tracing = OpenTelemetryTracingSetup(app, self.config)
        tracer_provider = tracing.setup_tracing()
        tracing.instrument_fastapi()

        # Set up OpenTelemetry metrics
        metrics = OpenTelemetryMetricsSetup(app, self.config)
        metrics.setup()
        meter = metrics.get_meter()
        
        # Add metrics middleware to FastAPI app
        app.add_middleware(MetricsMiddleware, meter=meter)

        return InstrumentationResult(
            meter=meter,
            logging_components=logging_components,
            tracer_provider=tracer_provider,
        )