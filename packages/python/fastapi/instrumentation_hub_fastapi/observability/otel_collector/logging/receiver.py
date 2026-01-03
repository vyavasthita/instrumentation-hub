"""Placeholder for log receiver configuration."""
from __future__ import annotations


class OTLPLogReceiver:
    """Keeps symmetry with older projects and leaves room for future protocols.

    Example:
        ```python
        receiver = OTLPLogReceiver()
        # Reserved for future configuration knobs.
        ```
    """

    def __init__(self):
        # Receiver setup is implicit in OpenTelemetry Python today.
        pass
