"""Quantigrade SDP Adapters Package.

Exports the 5 Canonical Adapters for MCP, OpenAPI, Agent Skills, Swarms BaseTools,
and Enterprise SaaS/ERP systems.
"""

from .enterprise_adapter import (
    N8NWebhookConnector,
    OdooERPConnector,
    SAPODataConnector,
    SQLDatabaseConnector,
)
from .mcp_adapter import MCPConnector
from .openapi_adapter import OpenAPIConnector
from .skill_adapter import AgentSkillConnector
from .swarm_adapter import SwarmToolConnector

__all__ = [
    "AgentSkillConnector",
    "MCPConnector",
    "N8NWebhookConnector",
    "OdooERPConnector",
    "OpenAPIConnector",
    "SAPODataConnector",
    "SQLDatabaseConnector",
    "SwarmToolConnector",
]
