# Instrumentation Hub – FastAPI Adapter

Helpers that wrap OpenTelemetry logging, tracing, and metrics instrumentation for FastAPI services.
The adapter bundles common configuration (OTLP exporters, Prometheus endpoint, request metrics middleware)
so a service only needs a few lines of code to emit full telemetry to OAAS or any OTLP collector.

---

## Installation

Until packages are published to an internal registry you can reference the Git repo directly:

```bash
poetry add git+https://github.com/<org>/instrumentation-hub.git#subdirectory=packages/python/fastapi
# or with pip
pip install "instrumentation-hub-fastapi @ git+https://github.com/<org>/instrumentation-hub.git@main#subdirectory=packages/python/fastapi"
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
| `OTEL_EXPORTER_LOGS_ENDPOINT` | OTLP HTTP endpoint for log exports (e.g. `http://otel-collector:4318/v1/logs`). |
| `OTEL_EXPORTER_TRACES_ENDPOINT` | OTLP HTTP endpoint for spans. |
| `OTEL_EXPORTER_METRICS_ENDPOINT` | OTLP HTTP endpoint for metrics. |
| `METRICS_MOUNT_PATH` | Path where the Prometheus exposition app is mounted (default `/metrics`). |
| `ATTACH_PYTHON_LOGGING` | When true, attaches the OTEL logging handler to the root logger. |

Default environment prefix is `OTEL_`, so variables such as `OTEL_EXPORTER_LOGS_ENDPOINT` and `OTEL_SERVICE_NAME` work
out of the box.

---

## Usage

```python
from fastapi import FastAPI
from instrumentation_hub_fastapi import Config, ConfigModel, setup_fastapi_instrumentation

app = FastAPI()

# Option 1: rely on environment variables and reuse the cached instance
config = Config()

# Option 2: override fields explicitly
# config = ConfigModel(
#     OTEL_SERVICE_NAME="orders-api",
#     OTEL_EXPORTER_LOGS_ENDPOINT="http://otel-collector:4318/v1/logs",
#     OTEL_EXPORTER_TRACES_ENDPOINT="http://otel-collector:4318/v1/traces",
#     OTEL_EXPORTER_METRICS_ENDPOINT="http://otel-collector:4318/v1/metrics",
# )

setup_fastapi_instrumentation(app, config)

@app.get("/health")
def health():
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
