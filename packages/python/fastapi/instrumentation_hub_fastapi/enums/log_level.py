from enum import Enum

class LogLevel(str, Enum):
    """Enum for log levels to avoid magic strings."""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"
