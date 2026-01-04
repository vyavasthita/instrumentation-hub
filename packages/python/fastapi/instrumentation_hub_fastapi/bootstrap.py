
"""Entrypoints for wiring Instrumentation Hub into FastAPI."""
from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI

from instrumentation_hub_fastapi.observability.otel_collector.logging.setup import OpenTelemetryLoggingSetup
from instrumentation_hub_fastapi.observability.otel_collector.metrics.middleware import MetricsMiddleware
from instrumentation_hub_fastapi.observability.otel_collector.metrics.setup import OpenTelemetryMetricsSetup
from instrumentation_hub_fastapi.observability.otel_collector.tracing.setup import OpenTelemetryTracingSetup
from instrumentation_hub_fastapi.enums.log_level import LogLevel


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
    def setup(self, app: FastAPI) -> InstrumentationResult:
        """
        Attach logging, tracing, metrics, and middleware to the provided FastAPI app.
        Returns an InstrumentationResult with meter, logging, and tracing objects.
        """
        # Set up OpenTelemetry logging
        logging_components = OpenTelemetryLoggingSetup().setup_logging()

        # Set up OpenTelemetry tracing
        tracing = OpenTelemetryTracingSetup(app)
        tracer_provider = tracing.setup_tracing()
        tracing.instrument_fastapi(tracer_provider=tracer_provider)

        # Set up OpenTelemetry metrics
        metrics = OpenTelemetryMetricsSetup(app)
        meter_provider = metrics.setup()
        metrics.instrument_fastapi(meter_provider)
        meter = OpenTelemetryMetricsSetup.get_meter(meter_provider)

        # Add metrics middleware to FastAPI app
        app.add_middleware(MetricsMiddleware, meter=meter)

        return InstrumentationResult(
            meter=meter,
            logging_components=logging_components,
            tracer_provider=tracer_provider,
        )