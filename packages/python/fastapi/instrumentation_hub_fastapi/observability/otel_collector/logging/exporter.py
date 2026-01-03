"""OTLP Log Exporter wrapper for Instrumentation Hub."""
from __future__ import annotations

from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter


class OTLPLogExporterWrapper:
    """Provides a lightweight layer over the OTLP log exporter."""

    def __init__(self, endpoint: str):
        self._exporter = OTLPLogExporter(endpoint=endpoint)

    def get_exporter(self) -> OTLPLogExporter:
        return self._exporter
