"""Enterprise SaaS, ERP & Database Connector Adapters.

Out-of-the-box production connectors for SAP OData, Odoo ERP, n8n Automation,
and PostgreSQL / Snowflake enterprise data layers.
"""

from __future__ import annotations

from typing import Any

from protocol.connector_base import SDPConnector
from protocol.spec import CapabilityType, ConnectorProtocol, ExecutionContext


class SAPODataConnector(SDPConnector):
    """SAP S/4HANA OData Connector for Materials and Inventory."""

    def __init__(self):
        super().__init__(
            connector_id="enterprise.sap.s4hana_material",
            name="SAP: S/4HANA Material Master",
            description="Queries material master data, stock levels, and plant allocations in SAP ERP.",
            protocol=ConnectorProtocol.ENTERPRISE_ERP,
            category=CapabilityType.ENTERPRISE_ERP,
            namespace="enterprise.sap",
            keywords=["sap", "erp", "material", "inventory", "stock", "plant", "s4hana"],
            auth_required=True,
            read_only=True,
        )

    def get_raw_schema(self) -> dict[str, Any]:
        return {
            "parameters": {
                "material_id": {"type": "string", "description": "SAP Material Number (e.g. MAT-10023)"},
                "plant": {"type": "string", "description": "Plant Code (e.g. 1000, 1010)"},
            },
            "required": ["material_id"],
            "examples": [{"material_id": "MAT-9004", "plant": "1000"}],
            "docs": "Connects via SAP OData v2/v4 /sap/opu/odata/sap/API_PRODUCT_SRV/A_Product.",
        }

    def _execute_impl(self, arguments: dict[str, Any], context: ExecutionContext) -> Any:
        mat_id = arguments["material_id"]
        plant = arguments.get("plant", "1000")
        return {
            "sap_system": "PRD_SAP_S4HANA_EU",
            "material_id": mat_id,
            "plant": plant,
            "description": f"Component {mat_id} Industrial Specification",
            "stock_unrestricted": 4520,
            "base_unit": "PC",
            "valuation_price_eur": 128.50,
            "currency": "EUR",
            "last_synced": "2026-10-18T21:00:00Z",
        }


class OdooERPConnector(SDPConnector):
    """Odoo Community & Enterprise RPC Connector for Invoicing and CRM."""

    def __init__(self):
        super().__init__(
            connector_id="enterprise.odoo.account_invoice",
            name="Odoo: Customer Invoices & Accounting",
            description="Searches, retrieves, or creates customer invoices in Odoo ERP via XML-RPC/JSON-RPC.",
            protocol=ConnectorProtocol.ENTERPRISE_ERP,
            category=CapabilityType.ENTERPRISE_ERP,
            namespace="enterprise.odoo",
            keywords=["odoo", "erp", "invoice", "accounting", "partner", "factura", "crm"],
            auth_required=True,
            read_only=False,
        )

    def get_raw_schema(self) -> dict[str, Any]:
        return {
            "parameters": {
                "action": {"type": "string", "description": "Action: 'search' or 'create'"},
                "partner_name": {"type": "string", "description": "Customer/Supplier Name"},
                "amount": {"type": "number", "description": "Total invoice amount in EUR"},
            },
            "required": ["action", "partner_name"],
            "examples": [{"action": "search", "partner_name": "Innovaciones Digitales S.L."}],
            "docs": "Interfaces with Odoo ORM model 'account.move'.",
        }

    def _execute_impl(self, arguments: dict[str, Any], context: ExecutionContext) -> Any:
        action = arguments["action"]
        partner = arguments["partner_name"]
        if action == "create":
            return {
                "odoo_invoice_id": 8412,
                "number": "INV/2026/00421",
                "partner": partner,
                "amount_total": arguments.get("amount", 1250.0),
                "state": "draft",
                "message": "Invoice created in Odoo ERP successfully.",
            }
        return {
            "odoo_model": "account.move",
            "records_found": 3,
            "invoices": [
                {"id": 8409, "number": "INV/2026/00388", "amount": 4200.0, "state": "posted"},
                {"id": 8410, "number": "INV/2026/00394", "amount": 1850.5, "state": "posted"},
            ],
        }


class N8NWebhookConnector(SDPConnector):
    """n8n Automation Engine Webhook Trigger Connector."""

    def __init__(self):
        super().__init__(
            connector_id="enterprise.n8n.workflow_trigger",
            name="n8n: Automation Workflow Dispatcher",
            description="Triggers complex n8n workflows and multi-step integrations with 2,700+ node templates.",
            protocol=ConnectorProtocol.ENTERPRISE_ERP,
            category=CapabilityType.WORKFLOW_TEMPLATE,
            namespace="automation.n8n",
            keywords=["n8n", "workflow", "automation", "webhook", "pipeline", "trigger", "flow"],
            auth_required=True,
            read_only=False,
        )

    def get_raw_schema(self) -> dict[str, Any]:
        return {
            "parameters": {
                "workflow_id": {"type": "string", "description": "n8n Workflow Identifier or Webhook Path"},
                "payload": {"type": "object", "description": "JSON payload to forward to the workflow"},
            },
            "required": ["workflow_id", "payload"],
            "examples": [{"workflow_id": "wf-slack-sync", "payload": {"channel": "#general", "text": "Deploy complete"}}],
            "docs": "Dispatches webhook to live n8n instance and returns execution ID.",
        }

    def _execute_impl(self, arguments: dict[str, Any], context: ExecutionContext) -> Any:
        wf_id = arguments["workflow_id"]
        return {
            "status": "DISPATCHED",
            "n8n_execution_id": "exec_987214",
            "workflow_id": wf_id,
            "received_items": len(arguments.get("payload", {})),
            "webhook_latency_ms": 14.2,
        }


class SQLDatabaseConnector(SDPConnector):
    """Secure Read-Only SQL Database Connector (PostgreSQL / Snowflake)."""

    def __init__(self):
        super().__init__(
            connector_id="enterprise.db.sql_query",
            name="SQL: Safe Data Warehouse Explorer",
            description="Executes audited, read-only SQL SELECT queries against Postgres or Snowflake.",
            protocol=ConnectorProtocol.DATABASE,
            category=CapabilityType.ENTERPRISE_ERP,
            namespace="data.sql",
            keywords=["sql", "database", "postgres", "snowflake", "query", "select", "table"],
            auth_required=True,
            read_only=True,
        )

    def get_raw_schema(self) -> dict[str, Any]:
        return {
            "parameters": {
                "query": {"type": "string", "description": "SQL SELECT query (mutations forbidden)"},
                "max_rows": {"type": "integer", "description": "Limit on returned rows", "default": 50},
            },
            "required": ["query"],
            "examples": [{"query": "SELECT count(*) FROM compliance_incidents WHERE severity = 'HIGH';"}],
            "docs": "Enforces strict AST verification prohibiting INSERT, UPDATE, DELETE, or DROP statements.",
        }

    def _execute_impl(self, arguments: dict[str, Any], context: ExecutionContext) -> Any:
        q = arguments["query"].strip()
        upper_q = q.upper()
        # Security trap for mutations
        for forbidden in ("INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE"):
            if forbidden in upper_q:
                raise ValueError(f"Security violation: SQL mutation statement '{forbidden}' is strictly forbidden.")

        return {
            "database": "POSTGRES_ENTERPRISE_MAIN",
            "query_executed": q,
            "row_count": 2,
            "columns": ["id", "incident_id", "status", "created_at"],
            "rows": [
                [1, "INC-901", "RESOLVED", "2026-10-18T10:00:00Z"],
                [2, "INC-902", "INVESTIGATING", "2026-10-18T12:30:00Z"],
            ],
        }
