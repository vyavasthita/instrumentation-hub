"""OTLP Log Exporter wrapper for Instrumentation Hub."""
from __future__ import annotations

from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter


class OTLPLogExporterWrapper:
    """Provides a lightweight layer over the OTLP log exporter.

    Example:
        ```python
        wrapper = OTLPLogExporterWrapper(endpoint="http://otel-collector:4318/v1/logs")
        exporter = wrapper.get_exporter()
        ```
    """

    def __init__(self, endpoint: str):
        self._exporter = OTLPLogExporter(endpoint=endpoint)

    def get_exporter(self) -> OTLPLogExporter:
        """Expose the configured exporter for use in processors or tests."""

        return self._exporter
