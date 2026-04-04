# Instrumentation Hub – FastAPI Adapter

OpenTelemetry instrumentation for FastAPI. Wraps logging, tracing, and metrics setup into a single call. Designed to push telemetry to [OAAS](https://github.com/vyavasthita/oaas).

**Example consumer:** [Auth Service](https://github.com/vyavasthita/auth-service) · **Parent repo:** [Instrumentation Hub](https://github.com/vyavasthita/instrumentation-hub)

---

## Install

```bash
poetry add git+https://github.com/vyavasthita/instrumentation-hub.git#subdirectory=packages/python/fastapi
# or
pip install "instrumentation-hub-fastapi @ git+https://github.com/vyavasthita/instrumentation-hub.git@main#subdirectory=packages/python/fastapi"
```

---

## Usage

```python
from fastapi import FastAPI
from instrumentation_hub_fastapi import FastAPIInstrumentation

app = FastAPI()
result = FastAPIInstrumentation().setup(app)
# result.meter, result.logging_components, result.tracer_provider available for advanced use
```

Set these env vars in your container:

```yaml
OTEL_EXPORTER_LOGS_ENDPOINT: http://otel-collector:4318/v1/logs
OTEL_EXPORTER_TRACES_ENDPOINT: http://otel-collector:4318/v1/traces
OTEL_EXPORTER_METRICS_ENDPOINT: http://otel-collector:4318/v1/metrics
OTEL_SERVICE_NAME: my-service
LOGGING_BACKEND: loki
TRACING_BACKEND: tempo
METRICS_BACKEND: prometheus
```

---

## What `.setup()` Configures

| Signal | What happens |
|--------|-------------|
| **Logging** | OTLP exporter + optional Python root logger attachment |
| **Tracing** | OTLP span exporter + FastAPI auto-instrumentation |
| **Metrics** | OTLP push + Prometheus `/metrics` endpoint |
| **Middleware** | Request/response JSON logging with sensitive field masking |
| **HTTP Metrics** | `http_server_requests_total` counter + `http_request_duration_seconds` histogram |

---

## Configuration

These env vars are set in the **consumer service's** `docker-compose.yaml` (not in this library). Endpoint values must point to the [OAAS](https://github.com/vyavasthita/oaas) OTel Collector on the shared Docker network. See [Auth Service](https://github.com/vyavasthita/auth-service) for a working example.

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_SERVICE_NAME` | `instrumentation-hub-fastapi` | Service identity |
| `OTEL_EXPORTER_LOGS_ENDPOINT` | `http://otel-collector:4318/v1/logs` | OTLP HTTP logs endpoint (OAAS Collector) |
| `OTEL_EXPORTER_TRACES_ENDPOINT` | `http://otel-collector:4318/v1/traces` | OTLP HTTP traces endpoint (OAAS Collector) |
| `OTEL_EXPORTER_METRICS_ENDPOINT` | `http://otel-collector:4318/v1/metrics` | OTLP HTTP metrics endpoint (OAAS Collector) |
| `LOGGING_BACKEND` | `loki` | OAAS log routing (`loki` / `opensearch`) |
| `TRACING_BACKEND` | `tempo` | OAAS trace routing (`tempo` / `jaeger`) |
| `METRICS_BACKEND` | `prometheus` | OAAS metrics routing |
| `METRICS_MOUNT_PATH` | `/metrics` | Prometheus exposition path |
| `ATTACH_PYTHON_LOGGING` | `true` | Attach OTEL handler to root logger |
| `LOG_LEVEL` | `INFO` | Python log level |

---

## Public API

```python
from instrumentation_hub_fastapi import (
    FastAPIInstrumentation,   # Main orchestrator
    InstrumentationResult,    # Returned by .setup()
    Config, ConfigModel,      # Configuration
    MetricsMiddleware,        # For custom meter usage
    rate_limited_log,         # Decorator to prevent log flooding
    LogLevel,                 # Enum
)
```

---

## Related Repositories

| Repository | Purpose |
|------------|---------|
| [OAAS](https://github.com/vyavasthita/oaas) | Observability stack (Grafana, Loki, Tempo, Prometheus) |
| [Auth Service](https://github.com/vyavasthita/auth-service) | Working example with full integration |

---

## License

Copyright © 2026 Dilip Kumar Sharma. All rights reserved.
