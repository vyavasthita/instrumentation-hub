# Instrumentation Hub

<p align="left">
  <img src="https://img.shields.io/badge/python-3.13-blue" alt="Python 3.13" />
  <img src="https://img.shields.io/badge/framework-FastAPI-009688" alt="FastAPI" />
  <img src="https://img.shields.io/badge/telemetry-OpenTelemetry-blueviolet" alt="OpenTelemetry" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License" />
</p>

An **OpenTelemetry Client Library**
- Add full observability (logs, traces, metrics) to any FastAPI service with a single function call.

### Why Instrumentation Hub?

- **One line to instrument.** Call `FastAPIInstrumentation().setup(app)` and your service gets structured logging, distributed tracing, HTTP metrics, and a Prometheus `/metrics` endpoint — all wired to [OAAS](https://github.com/vyavasthita/oaas).
- **Your service stays clean.** No OpenTelemetry boilerplate, no exporter setup, no log handler wiring. Observability is fully abstracted behind the library.
- **Sensitive data masking built in.** Request/response logging middleware automatically masks passwords, tokens, and configurable fields — safe for production from day one.
- **Backend routing via env vars.** Each service declares `LOGGING_BACKEND=loki`, `TRACING_BACKEND=tempo`, etc. The OAAS Collector routes accordingly — no code changes to switch backends.
- **Decoupled from infrastructure.** The library knows nothing about Grafana, Loki, or Prometheus. It pushes standard OTLP to whatever collector is on the Docker network.

```mermaid
flowchart LR
    subgraph Your Service
        App((FastAPI)) -- one function call --> IH[Instrumentation Hub]
        IH --> Logs[OTLP Logs]
        IH --> Traces[OTLP Traces]
        IH --> Metrics[OTLP Metrics + /metrics]
        IH --> MW[Request/Response Middleware]
    end
    Logs --> Collector[OAAS OTel Collector]
    Traces --> Collector
    Metrics --> Collector
    Collector --> Grafana[Grafana Stack]
```

**Example consumer:** [Auth Service](https://github.com/vyavasthita/auth-service)

---

## Skills Demonstrated

- **One-call instrumentation** — a single `.setup(app)` call configures OTLP exporters for logs, traces, and metrics plus auto-instrumentation middleware, eliminating hundreds of lines of boilerplate.
- **Sensitive data masking** — request/response logging middleware automatically redacts passwords, tokens, and configurable fields before export, production-safe from day one.
- **Environment-driven backend routing** — each service declares `LOGGING_BACKEND`, `TRACING_BACKEND`, `METRICS_BACKEND` as env vars; the library tags telemetry so the OAAS Collector routes signals to the correct backend.
- **Framework-agnostic core** — the FastAPI package wraps a framework-agnostic engine; adding Django support requires only a new adapter, not a rewrite.
- **Zero coupling to infrastructure** — the library pushes standard OTLP; it knows nothing about Grafana, Loki, or Prometheus, keeping consumer services vendor-neutral.

---

## Packages

| Package | Framework | Status |
|---------|-----------|--------|
| [instrumentation-hub-fastapi](packages/python/fastapi) | FastAPI | Active |
| instrumentation-hub-django | Django | Planned |

---

## Configuration

- These env vars are set in the **consumer service's** `docker-compose.yaml` (not in this library).
- Endpoint values must point to the [OAAS](https://github.com/vyavasthita/oaas) OTel Collector on the shared Docker network.
- See [Auth Service](https://github.com/vyavasthita/auth-service) for a working example.

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

## Quick Start (FastAPI)

### 1. Install

```bash
poetry add git+https://github.com/vyavasthita/instrumentation-hub.git#subdirectory=packages/python/fastapi
```

### 2. Wire

```python
from instrumentation_hub_fastapi import FastAPIInstrumentation

app = FastAPI()
FastAPIInstrumentation().setup(app)
```

That single `.setup()` call configures: OTLP log/trace/metric exporters, FastAPI auto-instrumentation, request/response logging middleware with sensitive field masking, HTTP metrics (counters + histograms), and a Prometheus `/metrics` endpoint.

## Related Repositories

| Repository | Purpose |
|------------|---------|
| [OAAS](https://github.com/vyavasthita/oaas) | Observability stack this library pushes telemetry to |
| [Auth Service](https://github.com/vyavasthita/auth-service) | Working example — JWT auth service using this library |
| [Micro-Cart](https://github.com/vyavasthita/micro-cart) | Working example — e-commerce microservices using this library |

---

## License

[MIT](LICENSE) — Copyright © 2026 Dilip Kumar Sharma.
