
"""Entrypoints for wiring Instrumentation Hub into FastAPI."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional

from fastapi import FastAPI

from .config import ConfigModel
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
        service_name: Optional[str] = None,
        exporter_logs_endpoint: Optional[str] = None,
        exporter_traces_endpoint: Optional[str] = None,
        exporter_metrics_endpoint: Optional[str] = None,
        metrics_mount_path: Optional[str] = None,
        attach_python_logging: Optional[bool] = None,
        log_level: LogLevel | str = LogLevel.INFO,
    ):
        """
        Accepts explicit configuration parameters for OpenTelemetry setup.
        All fields correspond to ConfigModel fields, but use snake_case for Pythonic API.
        """
        self.config = ConfigModel(
            OTEL_SERVICE_NAME=service_name,
            OTEL_EXPORTER_LOGS_ENDPOINT=exporter_logs_endpoint,
            OTEL_EXPORTER_TRACES_ENDPOINT=exporter_traces_endpoint,
            OTEL_EXPORTER_METRICS_ENDPOINT=exporter_metrics_endpoint,
            METRICS_MOUNT_PATH=metrics_mount_path,
            ATTACH_PYTHON_LOGGING=attach_python_logging,
            LOG_LEVEL=log_level,
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