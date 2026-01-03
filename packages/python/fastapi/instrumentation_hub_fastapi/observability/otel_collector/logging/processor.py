"""Log processor helpers."""
from __future__ import annotations

from opentelemetry.sdk._logs.export import BatchLogRecordProcessor


class OTLPLogProcessor:
    """Configures a batch log processor for OTLP exports.

    Example:
        ```python
        processor = OTLPLogProcessor(exporter_wrapper.get_exporter())
        provider.add_log_record_processor(processor.get_processor())
        ```
    """

    def __init__(self, exporter):
        self._processor = BatchLogRecordProcessor(exporter)

    def get_processor(self) -> BatchLogRecordProcessor:
        """Return the configured processor so callers can register it on providers."""

        return self._processor
