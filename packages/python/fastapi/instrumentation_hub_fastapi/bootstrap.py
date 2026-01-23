
"""Entrypoints for wiring Instrumentation Hub into FastAPI.

This module is usually the first thing application code touches, so it documents
the full observability story:

* Logging – configure an OTLP logger provider whose resource attributes include
    `logging_backend`, allowing the OAAS routing processor to pick the right
    exporter (Loki or OpenSearch).
* Tracing – install FastAPI instrumentation plus a tracer provider that emits
    spans to the Collector so Tempo dashboards work out of the box.
* Metrics – lazily create a shared `MeterProvider`, expose custom meters to the
    app, and mount both OTLP and Prometheus exporters so Grafana can scrape or
    receive pushes.
"""
from dataclasses import dataclass
from typing import Any
from fastapi import FastAPI

from instrumentation_hub_fastapi.observability.otel_collector.logging.setup import OpenTelemetryLoggingSetup
from instrumentation_hub_fastapi.observability.otel_collector.metrics.middleware import MetricsMiddleware
from instrumentation_hub_fastapi.observability.otel_collector.metrics.setup import OpenTelemetryMetricsSetup
from instrumentation_hub_fastapi.observability.otel_collector.tracing.setup import OpenTelemetryTracingSetup
from instrumentation_hub_fastapi.middlewares.api_instrumentation.config import InstrumentationConfigFactory, InstrumentationSanitizationConfig
from instrumentation_hub_fastapi.middlewares.api_instrumentation.api_instrumentation_middleware import ApiInstrumentationMiddleware


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
    """Configure logging, tracing, and metrics in one call.

    The helper intentionally hides the low-level OpenTelemetry plumbing so that
    each FastAPI project stays focused on business logic. It also guarantees
    that every signal shares the same `Resource` metadata, which is what allows
    OAAS' routing processor to recognize a service's chosen backends.

    Example:
        ```python
        app = FastAPI()
        FastAPIInstrumentation().setup(app)
        ```

    Under the hood this will wire the logging handler, register FastAPI
    middlewares, spin up OTLP exporters, and mount the `/metrics` endpoint.
    """
    def setup(
        self,
        app: FastAPI,
        metrics_config: InstrumentationConfigFactory = None,
        sanitization_config: InstrumentationSanitizationConfig = None,
        service_name: str = "instrumentation_hub",
        log_level: str = "INFO"
    ) -> InstrumentationResult:
        """Attach logging, tracing, metrics, and middleware to *app*.

        Returns
        -------
        InstrumentationResult
            Carries the three core providers so callers can register custom
            instruments, emit spans manually, or flush logs during shutdown.
        """
        # 1) Logging – attach the OTLP handler to Python's root logger so every
        # module automatically emits structured records that include
        # `logging_backend`. The OAAS collector uses that attribute to route
        # logs to Loki or OpenSearch without any per-service config files.
        logging_components = OpenTelemetryLoggingSetup().setup_logging()

        # 2) Tracing – instrument FastAPI before any routes run so request/route
        # span names and attributes follow OTEL semantic conventions.
        tracing = OpenTelemetryTracingSetup(app)
        tracer_provider = tracing.setup_tracing()
        tracing.instrument_fastapi(tracer_provider=tracer_provider)

        # 3) Metrics – expose both OTLP and Prometheus read paths so the
        # collector and Grafana can consume the exact same metrics.
        metrics = OpenTelemetryMetricsSetup(app)
        meter_provider = metrics.setup()
        metrics.instrument_fastapi(meter_provider)
        meter = OpenTelemetryMetricsSetup.get_meter(meter_provider)


        # 4) Middleware – add logging and metrics middleware for per-request instrumentation
        app.add_middleware(ApiInstrumentationMiddleware, config=metrics_config, sanitization_config=sanitization_config, service_name=service_name, log_level=log_level)
        app.add_middleware(MetricsMiddleware, meter=meter)

        return InstrumentationResult(
            meter=meter,
            logging_components=logging_components,
            tracer_provider=tracer_provider,
        )