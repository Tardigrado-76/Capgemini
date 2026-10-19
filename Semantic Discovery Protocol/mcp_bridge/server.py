"""Model Context Protocol (MCP) JSON-RPC Server Bridge.

Exposes the Semantic Discovery Protocol (SDP) as standard MCP tools,
enabling Claude Desktop, Cursor, and any MCP client to discover tools dynamically,
slashing context token consumption by up to 90% and executing safely.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from protocol.progressive_hydrator import ProgressiveHydrator
from protocol.registry import CapabilityRegistry
from protocol.semantic_router import SemanticRouter
from protocol.spec import ExecutionContext, RoutingQuery
from protocol.validator import MultiLevelValidator


class SDPProtocolMCPServer:
    """Standardized MCP endpoint wrapper for Semantic Discovery Protocol."""

    def __init__(self, registry: CapabilityRegistry | None = None):
        self.registry = registry or CapabilityRegistry()
        self.router = SemanticRouter(self.registry)
        self.hydrator = ProgressiveHydrator(self.registry)
        self.validator = MultiLevelValidator(self.registry)

    def list_mcp_tools(self) -> list[dict[str, Any]]:
        """Returns the formal MCP Tool definitions exported by SDP."""
        return [
            {
                "name": "sdp_discover",
                "description": "Discovers capabilities, skills, and connectors semantically from an intent query without context stuffing.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Natural language goal or task to accomplish"},
                        "top_k": {"type": "integer", "default": 5, "description": "Maximum number of candidate tools to return"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "sdp_hydrate",
                "description": "Progressively hydrates the full JSON parameter schema for a selected capability.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "capability_id": {"type": "string", "description": "ID of the capability discovered via sdp_discover"},
                        "detail_level": {"type": "string", "enum": ["minimal", "standard", "full"], "default": "standard"},
                    },
                    "required": ["capability_id"],
                },
            },
            {
                "name": "sdp_validate",
                "description": "Pre-validates proposed tool parameters before executing the target capability.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "capability_id": {"type": "string", "description": "Target capability ID"},
                        "arguments": {"type": "object", "description": "Dictionary of arguments to validate"},
                    },
                    "required": ["capability_id", "arguments"],
                },
            },
            {
                "name": "sdp_execute",
                "description": "Executes a validated capability or connector in a sandboxed, cryptographically audited environment.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "capability_id": {"type": "string", "description": "Target capability or connector ID"},
                        "arguments": {"type": "object", "description": "Dictionary of arguments to pass to the tool"},
                        "agent_id": {"type": "string", "default": "mcp_client", "description": "Calling agent identity"},
                        "correlation_id": {"type": "string", "default": "", "description": "Optional tracing or correlation ID"},
                    },
                    "required": ["capability_id", "arguments"],
                },
            },
        ]

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Dispatches an MCP tool call to the corresponding SDP handler."""
        if name == "sdp_discover":
            q = arguments.get("query", "")
            top_k = int(arguments.get("top_k", 5))
            matches = self.router.route(RoutingQuery(query=q, top_k=top_k))
            return {
                "status": "success",
                "matches": [m.model_dump() for m in matches],
                "tokens_consumed": len(matches) * 20,
            }

        elif name == "sdp_hydrate":
            cid = arguments.get("capability_id", "")
            detail = arguments.get("detail_level", "standard")
            hydrated = self.hydrator.hydrate(cid, detail_level=detail)
            if not hydrated:
                return {"status": "error", "message": f"Capability '{cid}' not found."}
            return {
                "status": "success",
                "schema": hydrated.model_dump(),
                "token_cost": hydrated.token_cost,
            }

        elif name == "sdp_validate":
            cid = arguments.get("capability_id", "")
            args = arguments.get("arguments", {})
            verdict = self.validator.validate(cid, args)
            return {
                "status": "success",
                "verdict": verdict.model_dump(),
            }

        elif name == "sdp_execute":
            cid = arguments.get("capability_id", "")
            args = arguments.get("arguments", {})
            agent_id = arguments.get("agent_id", "mcp_client")
            correlation_id = arguments.get("correlation_id", "")

            ctx = ExecutionContext(agent_id=agent_id, correlation_id=correlation_id)
            res = self.registry.execute(capability_id=cid, arguments=args, context=ctx)
            return {
                "status": "success" if res.success else "error",
                "result": res.model_dump(),
            }

        else:
            return {"status": "error", "message": f"Unknown MCP tool '{name}'"}

    def handle_json_rpc(self, request_str: str) -> str:
        """Processes a single JSON-RPC 2.0 string request and returns the response string."""
        try:
            req = json.loads(request_str)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "tools/list":
                result = {"tools": self.list_mcp_tools()}
                return json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result})

            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                tool_result = self.call_tool(tool_name, tool_args)
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(tool_result, default=str)}]},
                })

            elif method == "initialize":
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": "quantigrade-sdp-mcp-gateway", "version": "2.0.0"},
                        "capabilities": {"tools": {}},
                    },
                })

            else:
                return json.dumps({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method '{method}' not found"},
                })
        except Exception as ex:  # noqa: BLE001
            return json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": f"Internal JSON-RPC error: {ex}"},
            })

    def run_stdio(self) -> None:
        """Runs the server continuously reading from stdin and writing to stdout."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            response = self.handle_json_rpc(line)
            sys.stdout.write(response + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    server = SDPProtocolMCPServer()
    server.run_stdio()
