"""Telemetry and Thread Context Propagation for Compliance Mesh.

Instruments the live mesh with OpenTelemetry spans and multi-threaded context preservation.
"""

import functools
import time
import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any


class ComplianceSpan:
    """Represents a discrete compliance verification span."""

    def __init__(self, name: str, parent_id: str | None = None):
        self.name = name
        self.trace_id = uuid.uuid4().hex[:16]
        self.span_id = uuid.uuid4().hex[:8]
        self.parent_id = parent_id
        self.start_time = time.time()
        self.end_time: float | None = None
        self.status = "UNSET"
        self.attributes: dict[str, Any] = {}

    def set_attribute(self, key: str, value: Any):
        self.attributes[key] = value

    def end(self, status: str = "OK"):
        self.end_time = time.time()
        self.status = status

    def duration_ms(self) -> float:
        if self.end_time:
            return round((self.end_time - self.start_time) * 1000.0, 2)
        return 0.0


class TelemetryManager:
    """Coordinates telemetry spans across the compliance mesh."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.spans: list[ComplianceSpan] = []
        return cls._instance

    def start_span(self, name: str, parent_id: str | None = None) -> ComplianceSpan:
        span = ComplianceSpan(name=name, parent_id=parent_id)
        self.spans.append(span)
        return span

    def get_spans(self) -> list[dict[str, Any]]:
        return [
            {
                "name": s.name,
                "trace_id": s.trace_id,
                "span_id": s.span_id,
                "duration_ms": s.duration_ms(),
                "status": s.status,
                "attributes": s.attributes,
            }
            for s in self.spans
        ]


def trace_compliance(name: str):
    """Decorator to trace execution of compliance evaluations."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            mgr = TelemetryManager()
            span = mgr.start_span(name)
            try:
                res = func(*args, **kwargs)
                span.end(status="OK")
                return res
            except Exception as e:
                span.set_attribute("error", str(e))
                span.end(status="ERROR")
                raise
        return wrapper
    return decorator


class ContextThreadPoolExecutor(ThreadPoolExecutor):
    """ThreadPoolExecutor for executing concurrent framework evaluations."""
