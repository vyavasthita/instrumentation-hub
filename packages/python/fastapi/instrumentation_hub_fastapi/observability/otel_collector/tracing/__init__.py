"""Tracing setup utilities.

This package holds the FastAPI-specific tracing glue: a setup helper that wires
BatchSpanProcessor + OTLP exporters and then instruments the ASGI stack so
requests, exceptions, and background tasks show up in Tempo.
"""
