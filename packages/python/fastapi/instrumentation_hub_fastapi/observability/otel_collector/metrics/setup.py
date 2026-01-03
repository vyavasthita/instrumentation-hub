"""Metrics helpers for Instrumentation Hub's FastAPI adapter."""
from __future__ import annotations

from typing import Optional

from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from prometheus_client import make_asgi_app

from ....config import ConfigModel


class OpenTelemetryMetricsSetup:
    """Configure OTLP + Prometheus metrics for FastAPI."""

    def __init__(self, app, config: ConfigModel):
        self.app = app
        self.config = config
        self._meter_provider: Optional[MeterProvider] = None

    def setup(self) -> MeterProvider:
        endpoint = self.config.OTEL_EXPORTER_METRICS_ENDPOINT
        exporter = OTLPMetricExporter(endpoint=endpoint) if endpoint else None
        if exporter is None:
            raise ValueError("metrics_endpoint must be provided to enable metrics exports")

        otlp_reader = PeriodicExportingMetricReader(exporter)
        prom_reader = PrometheusMetricReader()

        provider = MeterProvider(
            resource=self.config.resource,
            metric_readers=[otlp_reader, prom_reader],
        )
        self._meter_provider = provider

        self.app.mount(self.config.METRICS_MOUNT_PATH, make_asgi_app())
        FastAPIInstrumentor.instrument_app(self.app, meter_provider=provider)
        return provider

    def get_meter(self):
        if not self._meter_provider:
            raise RuntimeError("MeterProvider not initialized. Call setup() first.")
        return self._meter_provider.get_meter(self.config.OTEL_SERVICE_NAME)
