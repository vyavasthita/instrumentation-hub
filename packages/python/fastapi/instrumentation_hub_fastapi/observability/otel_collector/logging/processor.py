"""Log processor helpers."""
from __future__ import annotations

from opentelemetry.sdk._logs.export import BatchLogRecordProcessor


class OTLPLogProcessor:
    """Configures a batch log processor for OTLP exports."""

    def __init__(self, exporter):
        self._processor = BatchLogRecordProcessor(exporter)

    def get_processor(self) -> BatchLogRecordProcessor:
        return self._processor
