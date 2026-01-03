# Instrumentation Hub

A polyglot toolkit for wiring OpenTelemetry-powered observability into any backend service.
The goal is to centralize best practices for exporters, resource configuration, and framework-specific helpers
so new projects can adopt logs, metrics, and traces with a single import regardless of language.

---

## Repository Layout

```
instrumentation-hub/
├── README.md
├── docs/                         # Deep dives, design decisions, and ADRs
├── examples/                     # Runnable samples that show end-to-end wiring
└── packages/
    ├── python/
    │   ├── fastapi/              # FastAPI-specific helpers (OTLP, Prometheus, etc.)
    │   │   └── instrumentation_hub_fastapi/
    │   └── django/               # Django-specific helpers (future work)
    │       └── instrumentation_hub_django/
    └── node/
        └── express/              # Placeholder for Node.js adapters (future work)
```

Each adapter lives in its own package so it can be published independently (e.g., `instrumentation-hub-fastapi`,
`instrumentation-hub-django`). Shared, framework-agnostic code will eventually sit in a core module that every adapter depends on.

- [FastAPI adapter docs](packages/python/fastapi/README.md) – installation and usage for `instrumentation-hub-fastapi`.

---

## Roadmap Snapshot

1. **Python / FastAPI**: Port the existing instrumentation glue code (OTLP exporters, Prometheus endpoint, middleware utilities).
2. **Python / Django**: Add request/response tracing middleware plus database metrics.
3. **Language-Agnostic Core**: Provide config schemas, semantic conventions, and exporter factories.
4. **Node.js / Express**: Ship a TypeScript helper that mirrors the Python feature set.
5. **Examples**: Maintain parity sample apps that emit telemetry into OAAS.

Open issues will track each milestone so additional contributors can grab a slice without touching every folder.

---

## Using This Toolkit in Other Services

You have a few installation options, depending on how formal you need versioning to be:

1. **Internal Package Index (recommended long-term)**
   - Publish each adapter to a private PyPI/Artifactory/Nexus feed under names like `instrumentation-hub-fastapi`.
   - Other repos simply run `poetry add instrumentation-hub-fastapi` or `pip install instrumentation-hub-fastapi==0.1.0`.
   - Gives you semantic versioning, changelogs, and easy rollbacks.

2. **Direct Git Dependency (fastest to bootstrap)**
   - Point Poetry or pip at the repo/tag: `poetry add git+https://github.com/vyavasthita/instrumentation-hub.git#subdirectory=packages/python/fastapi`.
   - No registry setup, but installs are slower and you need to manage tags carefully.

3. **Git Submodule / Monorepo Include**
   - Add this repo as a submodule and import the package source directly.
   - Keeps everything in sync but requires discipline when updating the submodule pointer.

4. **Source Vendoring (last resort)**
   - Copy the package folder into another service.
   - Only consider this if environments forbid git or registry access; otherwise upgrades become painful.

We'll start with option 2 (Git dependency) during development, then move to option 1 when the API stabilizes.

---

## Next Steps

- Add a `pyproject.toml` for the FastAPI adapter and migrate the instrumentation code from the tic-tac-toe backend.
- Build a minimal FastAPI example inside `examples/` that emits telemetry to OAAS to act as a regression harness.
- Document contribution guidelines (coding standards, testing strategy, release process).
- Set up CI (lint, type-check, unit tests, publish-on-tag).

Once the FastAPI adapter is stable, the Django and Express packages can mirror the same pattern.

---

## FastAPI Quick Start

```bash
poetry add git+https://github.com/vyavasthita/instrumentation-hub.git#subdirectory=packages/python/fastapi
```

```python
from fastapi import FastAPI
from instrumentation_hub_fastapi import setup_fastapi_instrumentation

app = FastAPI()
setup_fastapi_instrumentation(app)
```

Set the standard `OTEL_EXPORTER_*` env vars in your compose/service definition and the helper will emit logs, metrics, and traces directly to OAAS.
