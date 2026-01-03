"""Entrypoints for wiring Instrumentation Hub into FastAPI."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional

from fastapi import FastAPI

from .config import Config, ConfigModel
from .observability.otel_collector.logging.setup import OpenTelemetryLoggingSetup
from .observability.otel_collector.metrics.middleware import MetricsMiddleware
from .observability.otel_collector.metrics.setup import OpenTelemetryMetricsSetup
from .observability.otel_collector.tracing.setup import OpenTelemetryTracingSetup


@dataclass
class InstrumentationResult:
    meter: Any
    logging_components: Any
    tracer_provider: Any


class FastAPIInstrumentation:
    """High-level orchestration of logging, tracing, and metrics for FastAPI."""

    def __init__(self, config: Optional[ConfigModel] = None):
        self.config = config or Config()

    def setup(self, app: FastAPI) -> InstrumentationResult:
        logging_components = OpenTelemetryLoggingSetup(self.config).setup_logging()

        tracing = OpenTelemetryTracingSetup(app, self.config)
        tracer_provider = tracing.setup_tracing()
        tracing.instrument_fastapi()

        metrics = OpenTelemetryMetricsSetup(app, self.config)
        metrics.setup()
        meter = metrics.get_meter()
        app.add_middleware(MetricsMiddleware, meter=meter)

        return InstrumentationResult(
            meter=meter,
            logging_components=logging_components,
            tracer_provider=tracer_provider,
        )


def setup_fastapi_instrumentation(app: FastAPI, config: Optional[ConfigModel] = None) -> InstrumentationResult:
    """Convenience wrapper so callers can `setup_fastapi_instrumentation(app, config)`."""

    return FastAPIInstrumentation(config=config).setup(app)
