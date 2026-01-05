"""Logging setup for Instrumentation Hub.

`setup.py` wires the Python logging stack to OTLP, `exporter.py` and
`processor.py` wrap the OpenTelemetry classes, and `receiver.py` exists for API
symmetry (future protocols). Grouping them here keeps the public surface small
while still allowing thorough unit tests.
"""
