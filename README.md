# Instrumentation Hub

- OpenTelemetry client library for instrumenting backend services. 
- Configures OTLP exporters, middleware, and Prometheus endpoints so services can push telemetry to [OAAS](https://github.com/vyavasthita/oaas) with minimal code.

**Example consumer:** [Auth Service](https://github.com/vyavasthita/auth-service)

---

## Architecture

```mermaid
flowchart LR
    subgraph Your Service
        App((FastAPI)) --> IH[instrumentation-hub]
        IH --> Logs[OTLP Log Exporter]
        IH --> Traces[OTLP Span Exporter]
        IH --> Metrics[OTLP Metric Exporter + /metrics]
    end
    Logs --> Collector[OAAS OTel Collector]
    Traces --> Collector
    Metrics --> Collector
    Collector --> Grafana[Grafana Stack]
```

---

## Packages

| Package | Framework | Status |
|---------|-----------|--------|
| [instrumentation-hub-fastapi](packages/python/fastapi) | FastAPI | Active |
| instrumentation-hub-django | Django | Planned |

---

## Quick Start (FastAPI)

### Install

```bash
poetry add git+https://github.com/vyavasthita/instrumentation-hub.git#subdirectory=packages/python/fastapi
```

### Wire

```python
from instrumentation_hub_fastapi import FastAPIInstrumentation

app = FastAPI()
FastAPIInstrumentation().setup(app)
```

### Set env vars

```yaml
OTEL_EXPORTER_LOGS_ENDPOINT: http://otel-collector:4318/v1/logs
OTEL_EXPORTER_TRACES_ENDPOINT: http://otel-collector:4318/v1/traces
OTEL_EXPORTER_METRICS_ENDPOINT: http://otel-collector:4318/v1/metrics
OTEL_SERVICE_NAME: my-service
LOGGING_BACKEND: loki          # or opensearch
TRACING_BACKEND: tempo         # or jaeger
METRICS_BACKEND: prometheus
```

That single `.setup()` call configures: OTLP log/trace/metric exporters, FastAPI auto-instrumentation, request/response logging middleware with sensitive field masking, HTTP metrics (counters + histograms), and a Prometheus `/metrics` endpoint.

---

## Configuration

These env vars are set in the **consumer service's** `docker-compose.yaml` (not in this library). Endpoint values must point to the [OAAS](https://github.com/vyavasthita/oaas) OTel Collector on the shared Docker network. See [Auth Service](https://github.com/vyavasthita/auth-service) for a working example.

| Variable | Default | Description |
|----------|---------|-------------|
| `OTEL_SERVICE_NAME` | `instrumentation-hub-fastapi` | Service identity in telemetry |
| `OTEL_EXPORTER_LOGS_ENDPOINT` | `http://otel-collector:4318/v1/logs` | OTLP HTTP logs endpoint (OAAS Collector) |
| `OTEL_EXPORTER_TRACES_ENDPOINT` | `http://otel-collector:4318/v1/traces` | OTLP HTTP traces endpoint (OAAS Collector) |
| `OTEL_EXPORTER_METRICS_ENDPOINT` | `http://otel-collector:4318/v1/metrics` | OTLP HTTP metrics endpoint (OAAS Collector) |
| `LOGGING_BACKEND` | `loki` | Log routing hint for OAAS (`loki` / `opensearch`) |
| `TRACING_BACKEND` | `tempo` | Trace routing hint (`tempo` / `jaeger`) |
| `METRICS_BACKEND` | `prometheus` | Metrics routing hint |
| `METRICS_MOUNT_PATH` | `/metrics` | Prometheus exposition path |
| `ATTACH_PYTHON_LOGGING` | `true` | Attach OTEL handler to Python root logger |
| `LOG_LEVEL` | `INFO` | Python log level |

---

## Related Repositories

| Repository | Purpose |
|------------|---------|
| [OAAS](https://github.com/vyavasthita/oaas) | Observability stack this library pushes telemetry to |
| [Auth Service](https://github.com/vyavasthita/auth-service) | Working example of a service using this library |

---

## License

Copyright © 2026 Dilip Kumar Sharma. All rights reserved.
