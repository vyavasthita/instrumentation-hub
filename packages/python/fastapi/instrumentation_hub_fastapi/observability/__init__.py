"""Observability helpers shared by the FastAPI adapter.

The subpackages mirror the OpenTelemetry logical pipeline (collector receivers,
processors, exporters, etc.). Keeping them under `observability.*` makes it
obvious that these modules do not contain business logic—they are glue between
user code and the OAAS stack.
"""
