"""Unit and Integration Tests for Universal Connectors & Adapters.

Validates the full 4-Tier Progressive Disclosure lifecycle across:
- MCPConnector
- OpenAPIConnector
- AgentSkillConnector
- SwarmToolConnector
- Enterprise Connectors (SAP, Odoo, n8n, SQL)
- SDPProtocolMCPServer (JSON-RPC dispatch)
"""

import json

from mcp_bridge.server import SDPProtocolMCPServer
from protocol.adapters.mcp_adapter import MCPConnector
from protocol.adapters.openapi_adapter import OpenAPIConnector
from protocol.registry import CapabilityRegistry
from protocol.spec import (
    ConnectorProtocol,
)


def test_mcp_connector_lifecycle():
    mcp_schema = {
        "name": "weather_lookup",
        "description": "Fetch real-time weather and temperature for a city.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "default": "celsius"},
            },
            "required": ["city"],
        },
    }

    connector = MCPConnector(mcp_schema, namespace="external.weather")
    manifest = connector.manifest()

    assert manifest.id == "mcp.weather_lookup"
    assert manifest.protocol == ConnectorProtocol.MCP
    assert "city" in manifest.keywords or "weather_lookup" in manifest.keywords

    # Affinity
    score, reasons = connector.resolve_affinity("I need the weather in Madrid")
    assert score > 0.0
    assert len(reasons) > 0

    # Hydration
    hydrated = connector.hydrate(detail_level="standard")
    assert "city" in hydrated.parameters_schema

    # Validation
    verdict_valid = connector.validate_arguments({"city": "Madrid"})
    assert verdict_valid.valid is True
    assert len(verdict_valid.errors) == 0

    verdict_invalid = connector.validate_arguments({})
    assert verdict_invalid.valid is False
    assert any("city" in e for e in verdict_invalid.errors)

    # Execution
    res = connector.execute({"city": "Madrid"})
    assert res.success is True
    assert res.provenance_receipt is not None
    assert "Madrid" in str(res.data)


def test_openapi_connector_compilation():
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Test Payments API", "version": "1.0.0"},
        "paths": {
            "/charges": {
                "post": {
                    "operationId": "createCharge",
                    "summary": "Create a credit card charge",
                    "description": "Processes payment charges securely via gateway.",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "amount": {"type": "integer"},
                                        "currency": {"type": "string"},
                                    },
                                    "required": ["amount", "currency"],
                                }
                            }
                        }
                    },
                }
            }
        },
    }

    connectors = OpenAPIConnector.from_spec_dict(spec, namespace="payments.gateway")
    assert len(connectors) == 1

    conn = connectors[0]
    manifest = conn.manifest()
    assert manifest.id == "openapi.createCharge"
    assert manifest.protocol == ConnectorProtocol.OPENAPI

    # Validation and Execution
    verdict = conn.validate_arguments({"amount": 5000, "currency": "eur"})
    assert verdict.valid is True

    res = conn.execute({"amount": 5000, "currency": "eur"})
    assert res.success is True
    assert res.provenance_receipt is not None


def test_enterprise_connectors():
    registry = CapabilityRegistry(auto_discover_skills=False)

    # SAP OData
    sap_id = "enterprise.sap.s4hana_material"
    sap = registry.get_connector(sap_id)
    assert sap is not None
    res_sap = registry.execute(sap_id, {"material_id": "MAT-99", "plant": "1000"})
    assert res_sap.success is True
    assert "stock_unrestricted" in res_sap.data

    # Odoo ERP
    odoo_id = "enterprise.odoo.account_invoice"
    odoo = registry.get_connector(odoo_id)
    assert odoo is not None
    res_odoo = registry.execute(odoo_id, {"action": "search", "partner_name": "Innovaciones"})
    assert res_odoo.success is True
    assert "invoices" in res_odoo.data

    # n8n Webhook
    n8n_id = "enterprise.n8n.workflow_trigger"
    n8n = registry.get_connector(n8n_id)
    assert n8n is not None
    res_n8n = registry.execute(n8n_id, {"workflow_id": "wf-dora-01", "payload": {"test": 1}})
    assert res_n8n.success is True

    # SQL Relational Query
    sql_id = "enterprise.db.sql_query"
    sql = registry.get_connector(sql_id)
    assert sql is not None
    res_sql = registry.execute(sql_id, {"query": "SELECT * FROM users LIMIT 1;"})
    assert res_sql.success is True


def test_mcp_server_json_rpc_loop():
    server = SDPProtocolMCPServer()

    # Test tools/list
    list_req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
    list_res = json.loads(server.handle_json_rpc(list_req))
    assert "result" in list_res
    tool_names = [t["name"] for t in list_res["result"]["tools"]]
    assert "sdp_discover" in tool_names
    assert "sdp_hydrate" in tool_names
    assert "sdp_validate" in tool_names
    assert "sdp_execute" in tool_names

    # Test sdp_discover via tools/call
    disc_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "sdp_discover",
            "arguments": {"query": "SAP stock material", "top_k": 2},
        },
    })
    disc_res = json.loads(server.handle_json_rpc(disc_req))
    parsed_content = json.loads(disc_res["result"]["content"][0]["text"])
    assert parsed_content["status"] == "success"
    assert len(parsed_content["matches"]) > 0

    # Test sdp_execute via tools/call
    exec_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "sdp_execute",
            "arguments": {
                "capability_id": "enterprise.sap.s4hana_material",
                "arguments": {"material_id": "MAT-01", "plant": "1000"},
            },
        },
    })
    exec_res = json.loads(server.handle_json_rpc(exec_req))
    parsed_exec = json.loads(exec_res["result"]["content"][0]["text"])
    assert parsed_exec["status"] == "success"
    assert parsed_exec["result"]["success"] is True
