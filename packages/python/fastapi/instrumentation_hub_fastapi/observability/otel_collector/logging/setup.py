"""Logging utilities for Instrumentation Hub's FastAPI adapter."""
import atexit
import logging
from dataclasses import dataclass
from typing import Optional

from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

from instrumentation_hub_fastapi.config import Config
from instrumentation_hub_fastapi.observability.otel_collector.logging.exporter import OTLPLogExporterWrapper
from instrumentation_hub_fastapi.observability.otel_collector.logging.processor import OTLPLogProcessor


@dataclass
class LoggingComponents:
    """Bundle of logging objects returned to callers."""
    provider: LoggerProvider
    processor: BatchLogRecordProcessor


class OpenTelemetryLoggingSetup:
    """Wire OTLP logging into the current process.

    All configuration is read from environment variables via Config().

    Example:
        ```python
        setup = OpenTelemetryLoggingSetup()
        components = setup.setup_logging()
        ```
    """

    def __init__(self):
        """No config passed; reads from Config()."""
        self.components: Optional[LoggingComponents] = None

    def _create_logging_components(self) -> LoggingComponents:
        """Create and configure OTLP exporter, processor, and provider.

        The exporter talks directly to the OAAS collector. Because the provider
        is created with `Config().resource`, every log record carries
        `logging_backend`, which the collector's routing processor inspects
        before deciding whether to push to Loki or OpenSearch.
        """
        exporter_wrapper = OTLPLogExporterWrapper(endpoint=Config().OTEL_EXPORTER_LOGS_ENDPOINT)
        processor = OTLPLogProcessor(exporter_wrapper.get_exporter()).get_processor()
        provider = LoggerProvider(resource=Config().resource)
        provider.add_log_record_processor(processor)
        set_logger_provider(provider)
        return LoggingComponents(provider=provider, processor=processor)

    def _attach_python_logging(self, provider: LoggerProvider) -> None:
        """Attach OpenTelemetry LoggingHandler to the root logger if configured.

        Doing this once at bootstrap time means *every* module in the service,
        including third-party dependencies, now emits enriched OTLP records.
        This is how a simple `logging.info` call in application code ends up in
        Grafana Explore alongside its trace/span IDs.
        """
        handler = LoggingHandler(level=Config().LOG_LEVEL, logger_provider=provider)

        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(Config().LOG_LEVEL)
        root_logger.propagate = True

    def setup_logging(self) -> LoggingComponents:
        """Configure exporters, attach handlers, and register shutdown hooks."""
        self.components = self._create_logging_components()

        if Config().ATTACH_PYTHON_LOGGING:
            self._attach_python_logging(self.components.provider)

        atexit.register(self._shutdown)
        return self.components

    def _shutdown(self) -> None:
        """Flush buffered log records before interpreter exit."""
        if not self.components:
            return

        try:
            self.components.provider.shutdown()
        except Exception as exc:  # pragma: no cover - defensive logging path
            logging.error("Failed to shutdown OTEL logger provider: %s", exc)
