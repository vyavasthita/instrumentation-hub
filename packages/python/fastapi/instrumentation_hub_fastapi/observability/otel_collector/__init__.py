"""OTel collector integration helpers.

Every module under this namespace mirrors a concept that exists in the OAAS
collector configuration—logging, metrics, tracing, receivers, processors, and
exporters. This makes it easy to reason about how a change in code eventually
shows up in Grafana: the helper creates an OTLP exporter, the collector receives
it, and the routing processor uses the attributes injected by `Config.resource`.
"""