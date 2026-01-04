"""Configuration objects for FastAPI OpenTelemetry instrumentation."""
from __future__ import annotations

from functools import cached_property, lru_cache

from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from pydantic import Field
from pydantic_settings import BaseSettings


class ConfigModel(BaseSettings):
    """Typed configuration mirroring tic-tac-toe's pattern (uppercase fields).

    Example:
        ```python
        config = ConfigModel(OTEL_SERVICE_NAME="orders-api")
        print(config.OTEL_SERVICE_NAME)
        ```
    """
    LOGGING_BACKEND: str = Field(
        default="loki",
        description="Backend to use for logs (e.g., 'loki', 'none').",
    )
    TRACING_BACKEND: str = Field(
        default="tempo",
        description="Backend to use for traces (e.g., 'tempo', 'none').",
    )
    METRICS_BACKEND: str = Field(
        default="prometheus",
        description="Backend to use for metrics (e.g., 'prometheus', 'none').",
    )
    OTEL_SERVICE_NAME: str = Field(
        default="instrumentation-hub-fastapi",
        description="Value assigned to the OpenTelemetry service.name resource attribute.",
    )
    OTEL_EXPORTER_LOGS_ENDPOINT: str = Field(
        default="",
        description="OTLP HTTP endpoint that receives log records (e.g. http://otel-collector:4318/v1/logs).",
    )
    OTEL_EXPORTER_TRACES_ENDPOINT: str = Field(
        default="",
        description="OTLP HTTP endpoint that receives spans (e.g. http://otel-collector:4318/v1/traces).",
    )
    OTEL_EXPORTER_METRICS_ENDPOINT: str = Field(
        default="",
        description="OTLP HTTP endpoint that receives metric exports (e.g. http://otel-collector:4318/v1/metrics).",
    )
    METRICS_MOUNT_PATH: str = Field(
        default="/metrics",
        description="Path where the Prometheus exposition app will be mounted.",
    )
    ATTACH_PYTHON_LOGGING: bool = Field(
        default=True,
        description="Attach the OTEL logging handler to Python's root logger when True.",
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Log level for Python logging (e.g., 'INFO', 'DEBUG').",
    )

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

    @cached_property
    def resource(self) -> Resource:
        # Add per-signal backend resource attributes for routing processor.
        return Resource.create({
            SERVICE_NAME: self.OTEL_SERVICE_NAME,
            "logging_backend": self.LOGGING_BACKEND,
            "tracing_backend": self.TRACING_BACKEND,
            "metrics_backend": self.METRICS_BACKEND,
        })


@lru_cache
def Config() -> ConfigModel:
    """Return a cached configuration instance so repeated calls are cheap.

    Example:
        ```python
        config = Config()
        ```
    """

    return ConfigModel()


__all__ = ["Config", "ConfigModel"]
