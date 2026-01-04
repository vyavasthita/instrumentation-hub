"""Metrics helpers for Instrumentation Hub's FastAPI adapter."""
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from prometheus_client import make_asgi_app

from instrumentation_hub_fastapi.config import Config


class OpenTelemetryMetricsSetup:
    """Configure OTLP + Prometheus metrics for FastAPI.

    Example:
        ```python
        metrics = OpenTelemetryMetricsSetup(app)
        meter_provider = metrics.setup()
        metrics.instrument_fastapi(meter_provider)
        meter = OpenTelemetryMetricsSetup.get_meter(meter_provider)
        ```
    """

    def __init__(self, app):
        self.app = app

    def setup(self) -> MeterProvider:
        """Create exporters, mount the Prometheus endpoint, and return MeterProvider."""
        exporter = OTLPMetricExporter(endpoint=Config().OTEL_EXPORTER_METRICS_ENDPOINT)
        otlp_reader = PeriodicExportingMetricReader(exporter)
        prometheus_reader = PrometheusMetricReader()
        provider = MeterProvider(
            resource=Config().resource,
            metric_readers=[otlp_reader, prometheus_reader],
        )
        self.app.mount(Config().METRICS_MOUNT_PATH, make_asgi_app())
        return provider

    def instrument_fastapi(self, meter_provider: MeterProvider) -> None:
        """Register FastAPI instrumentation for metrics."""
        FastAPIInstrumentor.instrument_app(self.app, meter_provider=meter_provider)

    @staticmethod
    def get_meter(provider: MeterProvider):
        """Return the meter for user-defined instruments from the given provider."""
        return provider.get_meter(Config().OTEL_SERVICE_NAME)
