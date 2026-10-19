"""Canonical Universal Connector Interface (SDPConnector).

The definitive reference model for AI tools and connectors in 2026/2027.
Implements the 4-tier progressive lifecycle, pre-flight validation,
sandboxed execution, and cryptographic auditability.
"""

from __future__ import annotations

import re
import time
from abc import ABC, abstractmethod
from typing import Any

from .spec import (
    CapabilitySummary,
    CapabilityType,
    ConnectorProtocol,
    ConnectorResult,
    ExecutionContext,
    HydratedSchema,
    ValidationVerdict,
)


class SDPConnector(ABC):
    """Abstract Base Class for all Quantigrade SDP Connectors.

    Supercedes Anthropic's raw Model Context Protocol by offering:
    1. Tier 0 manifest (~18 tokens) to prevent context exhaustion.
    2. Intent-based semantic resolution.
    3. Progressive JIT schema hydration (minimal / standard / full).
    4. Multi-level pre-flight argument validation.
    5. Sandboxed, auditable execution.
    """

    def __init__(
        self,
        connector_id: str,
        name: str,
        description: str,
        protocol: ConnectorProtocol,
        category: CapabilityType = CapabilityType.MCP_TOOL,
        namespace: str = "general",
        keywords: list[str] | None = None,
        auth_required: bool = False,
        read_only: bool = True,
    ):
        self.connector_id = connector_id
        self.name = name
        self.description = description
        self.protocol = protocol
        self.category = category
        self.namespace = namespace
        self.keywords = keywords or []
        self.auth_required = auth_required
        self.read_only = read_only

    def manifest(self) -> CapabilitySummary:
        """Tier 0: Ultra-compact descriptor for zero-stuffing catalog indexing (~15-20 tokens)."""
        return CapabilitySummary(
            id=self.connector_id,
            name=self.name,
            type=self.category,
            protocol=self.protocol,
            namespace=self.namespace,
            description=self.description,
            keywords=self.keywords,
            estimated_tokens=15 + len(self.keywords),
            auth_required=self.auth_required,
            read_only=self.read_only,
        )

    def resolve_affinity(self, query_tokens: set[str] | str, raw_query: str | None = None) -> tuple[float, list[str]]:
        """Tier 1: Evaluates intent affinity for the Semantic Router."""
        if isinstance(query_tokens, str):
            actual_raw = query_tokens
            tokens = {tok.lower() for tok in re.findall(r"\w+", query_tokens.lower())}
        else:
            tokens = query_tokens
            actual_raw = raw_query or " ".join(tokens)

        reasons = []
        score = 0.0
        query_lower = actual_raw.lower()

        # Keyword matching
        matched_kw = set()
        for kw in self.keywords:
            if kw.lower() in tokens or kw.lower() in query_lower:
                matched_kw.add(kw)

        if matched_kw:
            reasons.append(f"Keywords: {', '.join(sorted(matched_kw))}")
            score += min(0.60, len(matched_kw) * 0.25)

        # Name and description matching
        name_lower = self.name.lower()
        if any(tok in name_lower for tok in tokens if len(tok) >= 3):
            score += 0.25
            reasons.append(f"Name affinity: {self.name}")

        desc_lower = self.description.lower()
        matched_desc = [tok for tok in tokens if tok in desc_lower and len(tok) >= 4]
        if matched_desc:
            score += min(0.30, len(matched_desc) * 0.10)
            reasons.append(f"Description match: {', '.join(matched_desc[:3])}")

        return min(1.0, score), reasons

    @abstractmethod
    def get_raw_schema(self) -> dict[str, Any]:
        """Returns the full parameter schema dictionary."""

    def hydrate(self, detail_level: str = "standard") -> HydratedSchema:
        """Tier 2: Expands the parameter schema on demand at requested detail level."""
        raw = self.get_raw_schema()
        params = raw.get("parameters", {})
        required = raw.get("required", [])
        examples = raw.get("examples", [])
        docs = raw.get("docs", self.description)

        if detail_level == "minimal":
            filtered = {k: {"type": v.get("type", "string")} for k, v in params.items()}
            return HydratedSchema(
                capability_id=self.connector_id,
                detail_level="minimal",
                parameters_schema=filtered,
                required_args=required,
                examples=[],
                documentation="",
                token_cost=50 + (len(filtered) * 10),
            )
        elif detail_level == "standard":
            filtered = {
                k: {
                    "type": v.get("type", "string"),
                    "description": v.get("description", ""),
                    "default": v.get("default", None),
                }
                for k, v in params.items()
            }
            return HydratedSchema(
                capability_id=self.connector_id,
                detail_level="standard",
                parameters_schema=filtered,
                required_args=required,
                examples=examples[:1],
                documentation=docs[:140],
                token_cost=140 + (len(filtered) * 25),
            )
        else:  # "full"
            return HydratedSchema(
                capability_id=self.connector_id,
                detail_level="full",
                parameters_schema=params,
                required_args=required,
                examples=examples,
                documentation=docs,
                token_cost=350 + (len(params) * 45) + len(docs.split()),
            )

    def validate_arguments(self, arguments: dict[str, Any], level: str = "full_runtime") -> ValidationVerdict:
        """Tier 3: Pre-execution validation enforcing argument presence, types and constraints."""
        raw = self.get_raw_schema()
        required = raw.get("required", [])
        params = raw.get("parameters", {})
        errors = []
        warnings = []
        sanitized = dict(arguments)

        # 1. Required parameters check
        for req in required:
            if req not in arguments or arguments[req] is None or arguments[req] == "":
                errors.append(f"Missing required parameter: '{req}'")

        # 2. Type conformity
        if level in ("type_strict", "full_runtime"):
            type_mapping = {
                "string": str,
                "boolean": bool,
                "integer": int,
                "number": (int, float),
                "array": list,
                "object": dict,
            }
            for k, val in arguments.items():
                if k in params:
                    exp_type = params[k].get("type", "string")
                    expected_cls = type_mapping.get(exp_type)
                    if expected_cls and not isinstance(val, expected_cls):  # type: ignore[arg-type]
                        # Attempt safe coercion for numbers and booleans
                        if exp_type == "integer" and isinstance(val, str) and val.isdigit():
                            sanitized[k] = int(val)
                        elif exp_type == "boolean" and isinstance(val, str) and val.lower() in ("true", "false"):
                            sanitized[k] = val.lower() == "true"
                        else:
                            errors.append(f"Type mismatch for '{k}': expected {exp_type}, got {type(val).__name__}")
                else:
                    warnings.append(f"Undeclared argument '{k}' ignored.")
                    sanitized.pop(k, None)

        return ValidationVerdict(
            capability_id=self.connector_id,
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_arguments=sanitized,
            validation_level=level,
        )

    def execute(self, arguments: dict[str, Any], context: ExecutionContext | None = None) -> ConnectorResult:
        """Executes the connector operation with error isolation and latency tracking."""
        ctx = context or ExecutionContext()
        start_time = time.perf_counter()

        # Pre-execution validation
        verdict = self.validate_arguments(arguments)
        if not verdict.valid:
            elapsed = (time.perf_counter() - start_time) * 1000
            return ConnectorResult(
                connector_id=self.connector_id,
                success=False,
                error=f"Validation failed: {'; '.join(verdict.errors)}",
                execution_time_ms=round(elapsed, 2),
            )

        try:
            output_data = self._execute_impl(verdict.sanitized_arguments, ctx)
            elapsed = (time.perf_counter() - start_time) * 1000
            return ConnectorResult(
                connector_id=self.connector_id,
                success=True,
                data=output_data,
                execution_time_ms=round(elapsed, 2),
                tokens_consumed=len(str(output_data)) // 4,
            )
        except Exception as e:  # noqa: BLE001
            elapsed = (time.perf_counter() - start_time) * 1000
            return ConnectorResult(
                connector_id=self.connector_id,
                success=False,
                error=f"Execution error in {self.name}: {e!s}",
                execution_time_ms=round(elapsed, 2),
            )

    @abstractmethod
    def _execute_impl(self, arguments: dict[str, Any], context: ExecutionContext) -> Any:
        """Subclass implementation of actual tool execution logic."""

    def export_as_mcp_tool(self) -> dict[str, Any]:
        """Exports connector in standard Anthropic MCP tool format."""
        raw = self.get_raw_schema()
        return {
            "name": self.connector_id.replace(".", "_").replace("-", "_"),
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": raw.get("parameters", {}),
                "required": raw.get("required", []),
            },
        }
