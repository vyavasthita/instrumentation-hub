"""Tracing utilities for Instrumentation Hub's FastAPI adapter."""
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from instrumentation_hub_fastapi.config import Config


class OpenTelemetryTracingSetup:
    """Configure tracing for FastAPI using OTLP exporters.

    Example:
        ```python
        tracing = OpenTelemetryTracingSetup(app)
        tracer_provider = tracing.setup_tracing()
        tracing.instrument_fastapi(tracer_provider)
        ```
    """
    def __init__(self, app):
        self.app = app

    def setup_tracing(self) -> TracerProvider:
        """Create the tracer provider, span processor, and exporter bindings."""
        endpoint = Config().OTEL_EXPORTER_TRACES_ENDPOINT
        exporter = OTLPSpanExporter(endpoint=endpoint)
        provider = TracerProvider(resource=Config().resource)
        span_processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(span_processor)
        trace.set_tracer_provider(provider)
        return provider

    def instrument_fastapi(self, tracer_provider: TracerProvider) -> None:
        """Register FastAPI instrumentation once setup is complete."""
        FastAPIInstrumentor.instrument_app(self.app, tracer_provider=tracer_provider)