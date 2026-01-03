"""Logging utilities for Instrumentation Hub's FastAPI adapter."""
from __future__ import annotations

import atexit
import logging
from dataclasses import dataclass
from typing import Optional

from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

from ....config import ConfigModel
from .exporter import OTLPLogExporterWrapper
from .processor import OTLPLogProcessor


@dataclass
class LoggingComponents:
    provider: LoggerProvider
    processor: BatchLogRecordProcessor


class OpenTelemetryLoggingSetup:
    """Wire OTLP logging into the current process."""

    def __init__(self, config: ConfigModel):
        self.config = config
        self.components: Optional[LoggingComponents] = None

    def setup_logging(self) -> LoggingComponents:
        if not self.config.OTEL_EXPORTER_LOGS_ENDPOINT:
            raise ValueError("OTEL_EXPORTER_LOGS_ENDPOINT must be provided to enable logging exports")

        exporter_wrapper = OTLPLogExporterWrapper(endpoint=self.config.OTEL_EXPORTER_LOGS_ENDPOINT)
        processor = OTLPLogProcessor(exporter_wrapper.get_exporter()).get_processor()
        provider = LoggerProvider(resource=self.config.resource)
        provider.add_log_record_processor(processor)
        set_logger_provider(provider)

        self.components = LoggingComponents(provider=provider, processor=processor)

        if self.config.ATTACH_PYTHON_LOGGING:
            handler = LoggingHandler(level=logging.INFO, logger_provider=provider)
            root_logger = logging.getLogger()
            root_logger.addHandler(handler)
            root_logger.setLevel(logging.INFO)
            root_logger.propagate = True

        atexit.register(self.shutdown)
        return self.components

    def shutdown(self) -> None:
        if not self.components:
            return
        try:
            self.components.provider.shutdown()
        except Exception as exc:  # pragma: no cover - defensive logging path
            logging.error("Failed to shutdown OTEL logger provider: %s", exc)
