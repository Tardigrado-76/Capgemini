"""MCP Connector Adapter.

Wraps standard Model Context Protocol (Anthropic MCP) tool schemas into
first-class Quantigrade SDPConnectors with progressive disclosure, validation,
and auditable execution.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from protocol.connector_base import SDPConnector
from protocol.spec import CapabilityType, ConnectorProtocol, ExecutionContext


class MCPConnector(SDPConnector):
    """Adapts standard MCP tool specifications into the 4-tier SDP model."""

    def __init__(
        self,
        tool_name: str | dict[str, Any],
        description: str = "",
        input_schema: dict[str, Any] | None = None,
        handler: Callable[[dict[str, Any]], Any] | None = None,
        server_id: str = "mcp_server",
        namespace: str = "tools.mcp",
        keywords: list[str] | None = None,
        read_only: bool = True,
    ):
        if isinstance(tool_name, dict):
            # Dict form: {"name": "...", "description": "...", "inputSchema": {...}}
            d = tool_name
            actual_name = d.get("name", "unnamed_tool")
            actual_desc = d.get("description", description)
            actual_schema = d.get("inputSchema", input_schema or {})
        else:
            actual_name = tool_name
            actual_desc = description
            actual_schema = input_schema or {}

        cid = f"mcp.{actual_name}" if server_id == "mcp_server" else f"mcp.{server_id}.{actual_name}"
        kw = keywords or [actual_name, "mcp"]
        # Extract properties as keywords too
        props = actual_schema.get("properties", {})
        kw.extend(list(props.keys())[:4])

        super().__init__(
            connector_id=cid,
            name=f"MCP: {actual_name}",
            description=actual_desc,
            protocol=ConnectorProtocol.MCP,
            category=CapabilityType.MCP_TOOL,
            namespace=namespace,
            keywords=list(set(kw)),
            auth_required=False,
            read_only=read_only,
        )
        self.input_schema = actual_schema
        self.handler = handler

    @classmethod
    def from_tool_dict(
        cls,
        tool_dict: dict[str, Any],
        server_id: str = "mcp_server",
        namespace: str = "tools.mcp",
        handler: Callable[[dict[str, Any]], Any] | None = None,
    ) -> MCPConnector:
        return cls(tool_dict, server_id=server_id, namespace=namespace, handler=handler)

    def get_raw_schema(self) -> dict[str, Any]:
        return {
            "parameters": self.input_schema.get("properties", {}),
            "required": self.input_schema.get("required", []),
            "examples": [],
            "docs": self.description,
        }

    def _execute_impl(self, arguments: dict[str, Any], context: ExecutionContext) -> Any:
        if self.handler:
            return self.handler(arguments)
        # Default mock simulation if no live remote socket
        return {
            "status": "success",
            "mcp_tool": self.name,
            "received_arguments": arguments,
            "dispatched_at": context.agent_id,
            "message": f"Tool '{self.name}' executed via MCP protocol.",
        }

    @classmethod
    def from_mcp_dict(cls, tool_dict: dict[str, Any], server_id: str = "default") -> MCPConnector:
        """Constructs an MCPConnector from a standard MCP tool json object."""
        return cls(
            tool_name=tool_dict.get("name", "unnamed_tool"),
            description=tool_dict.get("description", "No description provided"),
            input_schema=tool_dict.get("inputSchema", {}),
            server_id=server_id,
        )
