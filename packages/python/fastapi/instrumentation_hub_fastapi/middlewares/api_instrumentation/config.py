# This file was missing. Restoring config definitions for API instrumentation.
from enum import Enum, auto
from typing import Set

# Enum for supported metric types
class MetricType(Enum):
    REQUEST_COUNT = auto()
    REQUEST_LATENCY = auto()
    ERROR_COUNT = auto()
    # Add more as needed

# Config factory for instrumentation metrics
class InstrumentationConfigFactory:
    def __init__(self, enabled_metrics=None):
        """
        Args:
            enabled_metrics: List of MetricType enums to enable. If None, enables all defaults.
        """
        self.enabled_metrics = enabled_metrics or [
            MetricType.REQUEST_COUNT,
            MetricType.REQUEST_LATENCY,
            MetricType.ERROR_COUNT,
        ]

# Config for sanitization (sensitive fields and max field length)
class InstrumentationSanitizationConfig:
    DEFAULT_SENSITIVE_FIELDS: Set[str] = {'password', 'token', 'secret', 'authorization', 'cookie'}

    DEFAULT_EXCLUDED_HEADERS: Set[str] = {
        'accept',
        'accept-encoding',
        'accept-language',
        'connection',
        'content-length',
        'cookie',
        'origin',
        'referer',
        'sec-ch-ua',
        'sec-ch-ua-mobile',
        'sec-ch-ua-platform',
        'sec-fetch-dest',
        'sec-fetch-mode',
        'sec-fetch-site',
        'sec-gpc',
        'user-agent',
    }

    def __init__(self, sensitive_fields: Set[str] = None, max_field_length: int = 128, excluded_headers: Set[str] = None):
        """
        Args:
            sensitive_fields: set of field names to mask (case-insensitive). Defaults to common sensitive fields.
            max_field_length: int, max length for any field value
            excluded_headers: set of header names (lowercase) to exclude from logs. Defaults to noisy browser headers.
        """
        self.sensitive_fields: Set[str] = sensitive_fields or self.DEFAULT_SENSITIVE_FIELDS
        self.max_field_length: int = max_field_length
        self.excluded_headers: Set[str] = excluded_headers if excluded_headers is not None else self.DEFAULT_EXCLUDED_HEADERS
