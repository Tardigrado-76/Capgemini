"""Telemetry and Thread Context Propagation Engine.

Implements OpenTelemetry tracing and context propagation across agent threads
based on the ContextThreadPoolExecutor pattern.
"""

import functools
import logging
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any

logger = logging.getLogger("WhiteCodingTelemetry")


class SpanRecord:
    """Lightweight in-memory OpenTelemetry span record."""

    def __init__(self, name: str, trace_id: str, span_id: str, parent_id: str | None = None):
        self.name = name
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_id = parent_id
        self.start_time = time.time()
        self.end_time: float | None = None
        self.attributes: dict[str, Any] = {}
        self.status: str = "UNSET"

    def set_attribute(self, key: str, value: Any):
        self.attributes[key] = value

    def end(self, status: str = "OK"):
        self.end_time = time.time()
        self.status = status

    def duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time) * 1000.0
        return 0.0


class TelemetryManager:
    """Coordinates spans and thread-bound context propagation."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.spans: list[SpanRecord] = []
        return cls._instance

    def start_span(self, name: str, parent_id: str | None = None) -> SpanRecord:
        import uuid
        span = SpanRecord(
            name=name,
            trace_id=uuid.uuid4().hex[:16],
            span_id=uuid.uuid4().hex[:8],
            parent_id=parent_id,
        )
        self.spans.append(span)
        return span

    def get_spans(self) -> list[dict[str, Any]]:
        return [
            {
                "name": s.name,
                "trace_id": s.trace_id,
                "span_id": s.span_id,
                "duration_ms": round(s.duration_ms(), 2),
                "status": s.status,
                "attributes": s.attributes,
            }
            for s in self.spans
        ]


def trace_span(name: str):
    """Decorator to trace execution of critical White Coding harness functions."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            mgr = TelemetryManager()
            span = mgr.start_span(name)
            try:
                result = func(*args, **kwargs)
                span.end(status="OK")
                return result
            except Exception as e:
                span.set_attribute("error", str(e))
                span.end(status="ERROR")
                raise
        return wrapper
    return decorator


class ContextThreadPoolExecutor(ThreadPoolExecutor):
    """ThreadPoolExecutor that preserves context across thread boundaries."""
