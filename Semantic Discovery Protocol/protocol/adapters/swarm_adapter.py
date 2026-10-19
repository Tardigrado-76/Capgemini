"""Agency Swarm & Swarms Multi-Agent Tool Adapter.

Provides bidirectional interoperability:
1. Ingests Pydantic BaseTools into the 4-Tier SDPConnector registry.
2. Exports any SDPConnector into an AgencySwarm BaseTool or Swarms-compatible tool.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, create_model

from protocol.connector_base import SDPConnector
from protocol.spec import CapabilityType, ConnectorProtocol, ExecutionContext


class SwarmToolConnector(SDPConnector):
    """Adapts a Swarms / AgencySwarm tool into an SDPConnector."""

    def __init__(
        self,
        tool_name: str,
        description: str,
        parameters_model: type[BaseModel] | None = None,
        run_func: Callable[..., Any] | None = None,
        keywords: list[str] | None = None,
        namespace: str = "swarm.tools",
    ):
        cid = f"swarm.{tool_name.lower().replace(' ', '_')}"
        kw = keywords or [tool_name.lower(), "swarm", "agent_tool"]
        super().__init__(
            connector_id=cid,
            name=f"Swarm: {tool_name}",
            description=description,
            protocol=ConnectorProtocol.BASE_TOOL,
            category=CapabilityType.SWARM_BASE_TOOL,
            namespace=namespace,
            keywords=kw,
            auth_required=False,
            read_only=False,
        )
        self.parameters_model = parameters_model
        self.run_func = run_func

    def get_raw_schema(self) -> dict[str, Any]:
        if self.parameters_model:
            schema = self.parameters_model.model_json_schema()
            return {
                "parameters": schema.get("properties", {}),
                "required": schema.get("required", []),
                "examples": [],
                "docs": self.description,
            }
        return {
            "parameters": {"input_data": {"type": "string", "description": "Action input payload"}},
            "required": ["input_data"],
            "examples": [{"input_data": "example payload"}],
            "docs": self.description,
        }

    def _execute_impl(self, arguments: dict[str, Any], context: ExecutionContext) -> Any:
        if self.run_func:
            return self.run_func(**arguments)
        return {
            "status": "EXECUTED",
            "swarm_tool": self.name,
            "args": arguments,
            "agent_invoker": context.agent_id,
        }

    def to_swarm_callable(self) -> Callable[..., Any]:
        """Exports this connector as a callable function suitable for swarms.Agent(tools=[...])."""
        def _callable_tool(**kwargs) -> Any:
            res = self.execute(kwargs)
            if res.success:
                return res.data
            return f"Error: {res.error}"

        _callable_tool.__name__ = self.name.replace(" ", "_").replace(":", "_").lower()
        _callable_tool.__doc__ = self.description
        return _callable_tool

    def to_base_tool_class(self) -> type[BaseModel]:
        """Exports this connector as an AgencySwarm-compatible BaseTool class with a run() method."""
        raw = self.get_raw_schema()
        fields: dict[str, Any] = {}
        type_map = {
            "string": (str, ...),
            "integer": (int, ...),
            "number": (float, ...),
            "boolean": (bool, ...),
            "array": (list, ...),
            "object": (dict, ...),
        }

        for p_name, p_info in raw.get("parameters", {}).items():
            t_str = p_info.get("type", "string")
            is_req = p_name in raw.get("required", [])
            base_type = type_map.get(t_str, (str, ...))[0]
            if is_req:
                fields[p_name] = (base_type, ...)
            else:
                fields[p_name] = (base_type | None, p_info.get("default", None))

        model_cls = create_model(f"{self.name.replace(' ', '')}BaseTool", **fields)

        connector_ref = self
        def run(self_instance) -> Any:
            data = self_instance.model_dump()
            res = connector_ref.execute(data)
            return res.data if res.success else {"error": res.error}

        model_cls.run = run
        model_cls.__doc__ = self.description
        return model_cls
