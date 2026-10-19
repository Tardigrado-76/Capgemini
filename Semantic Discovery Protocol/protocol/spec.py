"""Semantic Discovery Protocol (SDP) Specification & Type Definitions.

Defines the formal RFC schemas for 4-tier progressive capability resolution
and the Canonical Universal Connector Reference Model.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CapabilityTier(str, Enum):
    """Progressive disclosure tiers in the SDP architecture."""
    TIER_0_INDEX = "tier_0_index"          # Zero-shot lightweight capability index (~15 tokens)
    TIER_1_ROUTED = "tier_1_routed"        # Ranked candidate capabilities (~30 tokens)
    TIER_2_HYDRATED = "tier_2_hydrated"    # Just-in-Time Schema Hydration (Minimal -> Full)
    TIER_3_VALIDATED = "tier_3_validated"  # Pre-execution argument verification


class CapabilityType(str, Enum):
    """Category of capability registered in the mesh."""
    AGENT_SKILL = "agent_skill"            # Portable SKILL.md folder with YAML frontmatter
    MCP_TOOL = "mcp_tool"                  # Model Context Protocol executable tool
    WORKFLOW_TEMPLATE = "workflow_template"# Enterprise automation template (e.g., n8n)
    OPENAPI_ENDPOINT = "openapi_endpoint"  # REST API endpoint from OpenAPI / Swagger spec
    SWARM_BASE_TOOL = "swarm_base_tool"    # AgencySwarm / Swarms Pydantic BaseTool
    ENTERPRISE_ERP = "enterprise_erp"      # SAP, Odoo, Salesforce, or Database connector


class ConnectorProtocol(str, Enum):
    """Underlying protocol of the connector."""
    MCP = "mcp"                            # Standard Model Context Protocol
    OPENAPI = "openapi"                    # OpenAPI 3.0 / 3.1 REST API
    AGENT_SKILL = "skill"                  # Antigravity SKILL.md specification
    BASE_TOOL = "base_tool"                # AgencySwarm / Swarms Tool
    ENTERPRISE_ERP = "enterprise_erp"      # SAP OData, Odoo XML-RPC, n8n webhook
    DATABASE = "database"                  # PostgreSQL, Snowflake, Elasticsearch SQL


class CapabilitySummary(BaseModel):
    """Tier 0: Ultra-compact capability descriptor (~15-20 tokens)."""
    id: str
    name: str
    type: CapabilityType = CapabilityType.MCP_TOOL
    protocol: ConnectorProtocol = ConnectorProtocol.MCP
    namespace: str = "general"
    description: str
    keywords: list[str] = Field(default_factory=list)
    estimated_tokens: int = 18
    auth_required: bool = False
    read_only: bool = True


class RoutingQuery(BaseModel):
    """Intent query submitted by an agent."""
    query: str
    top_k: int = 3
    filter_type: CapabilityType | None = None
    filter_protocol: ConnectorProtocol | None = None
    min_confidence: float = 0.20


class RoutingMatch(BaseModel):
    """Tier 1: Ranked match produced by the Semantic Router."""
    capability_id: str
    name: str
    type: CapabilityType
    confidence: float
    summary: str
    match_reasons: list[str] = Field(default_factory=list)
    estimated_tokens: int = 18


class HydratedSchema(BaseModel):
    """Tier 2: Just-in-time hydrated schema at requested detail level."""
    capability_id: str
    detail_level: str  # "minimal", "standard", "full"
    parameters_schema: dict[str, Any]
    required_args: list[str]
    examples: list[dict[str, Any]] = Field(default_factory=list)
    documentation: str = ""
    token_cost: int
    hydrated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ValidationVerdict(BaseModel):
    """Tier 3: Pre-execution validation scorecard."""
    capability_id: str
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    sanitized_arguments: dict[str, Any] = Field(default_factory=dict)
    validation_level: str = "full_runtime"


class ExecutionContext(BaseModel):
    """Runtime context passed into connector execution."""
    tenant_id: str = "default_tenant"
    agent_id: str = "orchestrator"
    correlation_id: str = ""
    credentials: dict[str, str] = Field(default_factory=dict)
    timeout_sec: float = 15.0
    sandbox_mode: bool = True
    audit_trail: bool = True


class ConnectorResult(BaseModel):
    """Execution output delivered back to the agent with cryptographic provenance."""
    connector_id: str
    success: bool
    data: Any = None
    error: str | None = None
    execution_time_ms: float = 0.0
    tokens_consumed: int = 0
    ed25519_signature: str | None = None
    block_hash: str | None = None
    executed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def provenance_receipt(self) -> dict[str, Any]:
        """Provides cryptographic audit receipt."""
        return {
            "connector_id": self.connector_id,
            "ed25519_signature": self.ed25519_signature or "ed25519_sig_simulated_slsa_l3",
            "block_hash": self.block_hash or "sha256_genesis_receipt",
            "executed_at": self.executed_at,
            "execution_time_ms": self.execution_time_ms,
        }

