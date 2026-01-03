"""Tracing utilities for Instrumentation Hub's FastAPI adapter."""
from __future__ import annotations

import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from ....config import ConfigModel


class OpenTelemetryTracingSetup:
    """Configure tracing for FastAPI using OTLP exporters.

    Example:
        ```python
        tracing = OpenTelemetryTracingSetup(app, config)
        tracing.setup_tracing()
        tracing.instrument_fastapi()
        ```
    """

    def __init__(self, app, config: ConfigModel):
        """Persist FastAPI app + config references for instrumentation hooks."""

        self.app = app
        self.config = config
        self.tracer_provider: Optional[TracerProvider] = None

    def setup_tracing(self) -> TracerProvider:
        """Create the tracer provider, span processor, and exporter bindings."""
        endpoint = self.config.OTEL_EXPORTER_TRACES_ENDPOINT
        exporter = OTLPSpanExporter(endpoint=endpoint) if endpoint else None
        if exporter is None:
            raise ValueError("traces_endpoint must be provided to enable tracing exports")

        provider = TracerProvider(resource=self.config.resource)
        span_processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(span_processor)
        trace.set_tracer_provider(provider)
        self.tracer_provider = provider
        return provider

    def instrument_fastapi(self) -> None:
        """Register FastAPI instrumentation once setup is complete."""

        if not self.tracer_provider:
            raise RuntimeError("Tracing not initialized. Call setup_tracing() first.")
        FastAPIInstrumentor.instrument_app(self.app, tracer_provider=self.tracer_provider)
        logging.info("OpenTelemetry tracing configured for FastAPI.")
