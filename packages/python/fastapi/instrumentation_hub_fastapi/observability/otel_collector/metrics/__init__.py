"""Metrics setup utilities.

Exports Prometheus + OTLP readers side-by-side so Grafana can scrape locally
while the collector still receives the full signal. See `setup.py` for the
exporters and `middleware.py` for per-request measurements.
"""
