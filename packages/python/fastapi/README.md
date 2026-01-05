# Instrumentation Hub – FastAPI Adapter

Helpers that wrap OpenTelemetry logging, tracing, and metrics instrumentation for FastAPI services.
The adapter bundles common configuration (OTLP exporters, Prometheus endpoint, request metrics middleware)
so a service only needs a few lines of code to emit full telemetry to OAAS or any OTLP collector.

---

## Installation

Until packages are published to an internal registry you can reference the public GitHub repo directly:

```bash
poetry add git+https://github.com/vyavasthita/instrumentation-hub.git#subdirectory=packages/python/fastapi
# or with pip
pip install "instrumentation-hub-fastapi @ git+https://github.com/vyavasthita/instrumentation-hub.git@main#subdirectory=packages/python/fastapi"
```

When published to PyPI/Artifactory the installation becomes:

```bash
poetry add instrumentation-hub-fastapi
```

---

## Configuration

`Config()` returns a cached `pydantic-settings` object (mirroring the tic-tac-toe backend) so you can load values from
environment variables without repeatedly instantiating it. You can also instantiate `ConfigModel` directly if you need
to override fields programmatically.
Supported fields:

| Field | Description |
|-------|-------------|
| `OTEL_SERVICE_NAME` | Resource attribute stored on spans/logs/metrics. |
| `LOGGING_BACKEND` | Hint for the OAAS collector routing processor (`loki` or `opensearch`). |
| `TRACING_BACKEND` | Hint for trace routing (`tempo` by default, set `jaeger` to fan out to Jaeger). |
| `METRICS_BACKEND` | Hint for metrics routing (`prometheus` today, extensible later). |
| `OTEL_EXPORTER_LOGS_ENDPOINT` | OTLP HTTP endpoint for log exports (e.g. `http://otel-collector:4318/v1/logs`). |
| `OTEL_EXPORTER_TRACES_ENDPOINT` | OTLP HTTP endpoint for spans. |
| `OTEL_EXPORTER_METRICS_ENDPOINT` | OTLP HTTP endpoint for metrics. |
| `METRICS_MOUNT_PATH` | Path where the Prometheus exposition app is mounted (default `/metrics`). |
| `ATTACH_PYTHON_LOGGING` | When true, attaches the OTEL logging handler to the root logger. |

Default environment prefix is `OTEL_`, so variables such as `OTEL_EXPORTER_LOGS_ENDPOINT` and `OTEL_SERVICE_NAME` work
out of the box.

> Every service sets its own `{LOGGING,TRACING,METRICS}_BACKEND` values, so the OAAS collector can host mixed
> combinations (e.g., Service A → Loki/Jaeger while Service B → OpenSearch/Tempo) without per-tenant config drift.

---

## Usage


```python
# Example: Instrumenting FastAPI with primitive parameters (no internal config dependency)
from fastapi import FastAPI
from instrumentation_hub_fastapi import setup_fastapi_instrumentation

app = FastAPI()

# Optionally load settings from your own config or environment
otel_traces_endpoint = "http://otel-collector:4318/v1/traces"
otel_logs_endpoint = "http://otel-collector:4318/v1/logs"
otel_metrics_endpoint = "http://otel-collector:4318/v1/metrics"
service_name = "orders-api"

# Attach OpenTelemetry logging, tracing, and metrics using primitive parameters
setup_fastapi_instrumentation(
    app,
    otlp_endpoint=otel_traces_endpoint,  # OTLP endpoint for traces
    service_name=service_name,
    log_level="INFO",  # Optionally set log level
    OTEL_EXPORTER_LOGS_ENDPOINT=otel_logs_endpoint,
    OTEL_EXPORTER_METRICS_ENDPOINT=otel_metrics_endpoint,
    METRICS_MOUNT_PATH="/metrics",
    ATTACH_PYTHON_LOGGING=True,
)

@app.get("/health")
def health():
    """Health check endpoint for service monitoring."""
    return {"status": "ok"}
```

This call sets up:
- OTLP log exporter (and optional Python logging handler)
- OTLP tracing with FastAPI instrumentation
- OTLP + Prometheus metrics plus `/metrics` route
- Request counter and latency histogram middleware

`setup_fastapi_instrumentation` returns an `InstrumentationResult` if you need access to the meter or providers.

---

## Roadmap

- Integration tests that spin up a FastAPI example and assert Loki/Tempo/Prometheus receive data.
- Additional middleware hooks (e.g., custom attributes, request IDs).
- Support toggles for Prometheus vs OTLP exports.
- Tutorial under `examples/fastapi/` demonstrating integration with OAAS.
