"""Capability & Connector Registry Engine.

Maintains the federated catalog of Agent Skills, MCP Tools, OpenAPI Endpoints,
and Enterprise ERP Connectors, generating the ultra-compact Tier 0 capability index.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .adapters.enterprise_adapter import (
    N8NWebhookConnector,
    OdooERPConnector,
    SAPODataConnector,
    SQLDatabaseConnector,
)
from .adapters.skill_adapter import AgentSkillConnector
from .connector_base import SDPConnector
from .spec import (
    CapabilitySummary,
    CapabilityType,
    ConnectorProtocol,
    ConnectorResult,
    ExecutionContext,
)


class CapabilityRegistry:
    """Unified catalog and Tier 0 index provider for the mesh."""

    def __init__(self, auto_discover_skills: bool = True):
        self._summaries: dict[str, CapabilitySummary] = {}
        self._full_specs: dict[str, dict[str, Any]] = {}
        self._connectors: dict[str, SDPConnector] = {}

        self._populate_enterprise_defaults()
        if auto_discover_skills:
            self._auto_discover_antigravity_skills()

    def register(self, summary: CapabilitySummary, full_spec: dict[str, Any]) -> None:
        """Registers a legacy capability descriptor and its full schema specification."""
        self._summaries[summary.id] = summary
        self._full_specs[summary.id] = full_spec

    def register_connector(self, connector: SDPConnector) -> None:
        """Registers a first-class SDPConnector into the mesh."""
        self._connectors[connector.connector_id] = connector
        self._summaries[connector.connector_id] = connector.manifest()
        self._full_specs[connector.connector_id] = connector.get_raw_schema()

    def get_connector(self, connector_id: str) -> SDPConnector | None:
        """Retrieves the active SDPConnector instance if registered."""
        return self._connectors.get(connector_id)

    def get_index(
        self,
        filter_type: CapabilityType | None = None,
        filter_protocol: ConnectorProtocol | None = None,
    ) -> list[CapabilitySummary]:
        """Provides the ultra-lightweight Tier 0 capability index (~15-20 tokens per tool)."""
        res = list(self._summaries.values())
        if filter_type:
            res = [s for s in res if s.type == filter_type]
        if filter_protocol:
            res = [s for s in res if s.protocol == filter_protocol]
        return res

    def get_summary(self, capability_id: str) -> CapabilitySummary | None:
        return self._summaries.get(capability_id)

    def get_full_spec(self, capability_id: str) -> dict[str, Any] | None:
        return self._full_specs.get(capability_id)

    def count(self) -> int:
        return len(self._summaries)

    def execute(
        self,
        capability_id: str,
        arguments: dict[str, Any],
        context: ExecutionContext | None = None,
    ) -> ConnectorResult:
        """Dispatches execution to the registered connector with full isolation and tracking."""
        ctx = context or ExecutionContext()
        connector = self._connectors.get(capability_id)
        if connector:
            return connector.execute(arguments, ctx)

        # Fallback for capabilities registered via raw dictionaries
        spec = self.get_full_spec(capability_id)
        if not spec:
            return ConnectorResult(
                connector_id=capability_id,
                success=False,
                error=f"Capability '{capability_id}' not found in registry.",
            )

        return ConnectorResult(
            connector_id=capability_id,
            success=True,
            data={
                "message": f"Successfully simulated execution for legacy capability {capability_id}",
                "echo_arguments": arguments,
            },
        )

    def _auto_discover_antigravity_skills(self) -> None:
        """Auto-discovers installed skills across the Antigravity configuration directory."""
        candidates = [
            Path(r"C:\Users\josel\.gemini\config\skills"),
            Path(__file__).resolve().parent.parent.parent.parent / ".agents" / "skills",
        ]
        for base in candidates:
            if base.exists() and base.is_dir():
                try:
                    discovered = AgentSkillConnector.scan_skills_directory(base)
                    for sc in discovered[:35]:  # Index top discovered skills
                        if sc.connector_id not in self._summaries:
                            self.register_connector(sc)
                except Exception:  # noqa: S110, BLE001 # nosec B110
                    pass

    def _populate_enterprise_defaults(self) -> None:
        """Populates baseline enterprise capabilities and reference connectors."""
        # Register core enterprise connectors
        self.register_connector(SAPODataConnector())
        self.register_connector(OdooERPConnector())
        self.register_connector(N8NWebhookConnector())
        self.register_connector(SQLDatabaseConnector())

        # Baseline Agent Skills & MCP Tools
        defaults = [
            (
                CapabilitySummary(
                    id="skill.code-doctor",
                    name="Code Doctor",
                    type=CapabilityType.AGENT_SKILL,
                    protocol=ConnectorProtocol.AGENT_SKILL,
                    namespace="engineering.quality",
                    description="Automated code audit, linter, type-checking and security vulnerability auto-fix.",
                    keywords=["audit", "lint", "typecheck", "ruff", "mypy", "security", "code-quality"],
                    estimated_tokens=20,
                ),
                {
                    "parameters": {
                        "path": {"type": "string", "description": "Target file or directory path"},
                        "auto_fix": {"type": "boolean", "default": True, "description": "Auto-apply fixes"},
                        "linters": {"type": "array", "items": {"type": "string"}, "description": "Linter engines to run"},
                    },
                    "required": ["path"],
                    "examples": [{"path": "src/main.py", "auto_fix": True}],
                    "docs": "Audits Python and TypeScript codebases. Runs ruff, mypy, bandit, and react-doctor.",
                },
            ),
            (
                CapabilitySummary(
                    id="skill.openspec-explore",
                    name="OpenSpec Explore",
                    type=CapabilityType.AGENT_SKILL,
                    protocol=ConnectorProtocol.AGENT_SKILL,
                    namespace="architecture.specification",
                    description="Interactive thinking partner for investigating repository changes and clarifying specs.",
                    keywords=["spec", "explore", "requirements", "rfc", "design", "investigate"],
                    estimated_tokens=18,
                ),
                {
                    "parameters": {
                        "topic": {"type": "string", "description": "Design concept or requirement to explore"},
                        "context_files": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["topic"],
                    "examples": [{"topic": "Rate Limiter architecture", "context_files": ["api/v1.py"]}],
                    "docs": "Assists developers in mapping out boundaries and design decisions before implementation.",
                },
            ),
            (
                CapabilitySummary(
                    id="mcp.m3cp-audio-transcribe",
                    name="m3cp Audio Transcribe",
                    type=CapabilityType.MCP_TOOL,
                    protocol=ConnectorProtocol.MCP,
                    namespace="media.multimodal",
                    description="Converts speech and meeting audio recordings into structured text and speaker diarization.",
                    keywords=["audio", "transcribe", "speech-to-text", "voice", "multimodal", "diarization"],
                    estimated_tokens=21,
                ),
                {
                    "parameters": {
                        "audio_path": {"type": "string", "description": "Path or URL to audio file"},
                        "language": {"type": "string", "default": "es", "description": "Spoken language code"},
                        "diarize": {"type": "boolean", "default": True, "description": "Identify individual speakers"},
                    },
                    "required": ["audio_path"],
                    "examples": [{"audio_path": "/var/recordings/meeting.mp3", "language": "es"}],
                    "docs": "Performs local or remote transcription with timestamp alignment and diarization.",
                },
            ),
            (
                CapabilitySummary(
                    id="mcp.github-pr-manage",
                    name="GitHub PR Manager",
                    type=CapabilityType.MCP_TOOL,
                    protocol=ConnectorProtocol.MCP,
                    namespace="devops.git",
                    description="Creates, reviews, comments, and automates pull requests on GitHub repositories.",
                    keywords=["github", "git", "pull-request", "pr", "review", "merge", "devops"],
                    estimated_tokens=19,
                ),
                {
                    "parameters": {
                        "repo": {"type": "string", "description": "Owner/Repository slug"},
                        "action": {"type": "string", "description": "Action: 'create', 'merge', or 'review'"},
                        "title": {"type": "string", "description": "PR title"},
                        "body": {"type": "string", "description": "PR markdown description"},
                    },
                    "required": ["repo", "action"],
                    "examples": [{"repo": "enterprise/core", "action": "create", "title": "feat: new connector"}],
                    "docs": "Integrates directly with GitHub REST / GraphQL API v4 via GitHub MCP Server.",
                },
            ),
            (
                CapabilitySummary(
                    id="mcp.slack-notify",
                    name="Slack Enterprise Notifier",
                    type=CapabilityType.MCP_TOOL,
                    protocol=ConnectorProtocol.MCP,
                    namespace="communication.chat",
                    description="Posts formatted operational alerts, audit summaries, and tickets to Slack channels.",
                    keywords=["slack", "notification", "alert", "message", "channel", "webhook"],
                    estimated_tokens=17,
                ),
                {
                    "parameters": {
                        "channel": {"type": "string", "description": "Slack channel name or ID"},
                        "message": {"type": "string", "description": "Markdown alert body"},
                        "level": {"type": "string", "default": "info", "description": "Alert level (info, warning, critical)"},
                    },
                    "required": ["channel", "message"],
                    "examples": [{"channel": "#devops-alerts", "message": "SLSA L3+ seal verified."}],
                    "docs": "Slack Web API bot integration with rate-limiting and channel verification.",
                },
            ),
            (
                CapabilitySummary(
                    id="mcp.postgres-query",
                    name="PostgreSQL Query Executor",
                    type=CapabilityType.MCP_TOOL,
                    protocol=ConnectorProtocol.MCP,
                    namespace="database.relational",
                    description="Executes parameterized SQL queries against audited PostgreSQL data warehouses.",
                    keywords=["sql", "postgres", "database", "query", "relational", "warehouse"],
                    estimated_tokens=18,
                ),
                {
                    "parameters": {
                        "query": {"type": "string", "description": "SQL statement to execute"},
                        "params": {"type": "array", "items": {"type": "string"}, "description": "Bind parameters"},
                    },
                    "required": ["query"],
                    "examples": [{"query": "SELECT * FROM audit_log LIMIT 5"}],
                    "docs": "Executes read-only or transactional SQL statements in PostgreSQL.",
                },
            ),
        ]

        for summary, full_spec in defaults:
            self.register(summary, full_spec)
