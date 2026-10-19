"""Antigravity Agent Skill Connector Adapter.

Discovers and ingests SKILL.md folders (with YAML frontmatter) across the
Antigravity IDE environment and transforms them into standard SDPConnectors.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from protocol.connector_base import SDPConnector
from protocol.spec import CapabilityType, ConnectorProtocol, ExecutionContext


class AgentSkillConnector(SDPConnector):
    """Wraps an Antigravity SKILL.md agent capability into an SDP connector."""

    def __init__(
        self,
        skill_id: str,
        name: str,
        description: str,
        skill_path: str,
        parameters_schema: dict[str, Any] | None = None,
        keywords: list[str] | None = None,
        namespace: str = "skills.antigravity",
    ):
        cid = f"skill.{skill_id}"
        kw = keywords or [skill_id.replace("-", " "), "skill", "agent"]
        kw.extend(name.lower().split())

        super().__init__(
            connector_id=cid,
            name=f"Skill: {name}",
            description=description,
            protocol=ConnectorProtocol.AGENT_SKILL,
            category=CapabilityType.AGENT_SKILL,
            namespace=namespace,
            keywords=list(set(kw)),
            auth_required=False,
            read_only=True,
        )
        self.skill_path = skill_path
        self.parameters_schema = parameters_schema or {
            "query": {"type": "string", "description": "Goal or instruction to delegate to this skill"},
            "context_files": {"type": "array", "description": "List of relevant files or artifacts"},
        }

    def get_raw_schema(self) -> dict[str, Any]:
        return {
            "parameters": self.parameters_schema,
            "required": ["query"],
            "examples": [{"query": f"Execute {self.name} workflow"}],
            "docs": f"Skill path: {self.skill_path}\n{self.description}",
        }

    def _execute_impl(self, arguments: dict[str, Any], context: ExecutionContext) -> Any:
        query = arguments.get("query", "")
        return {
            "status": "DISPATCHED_TO_SKILL",
            "skill_id": self.connector_id,
            "skill_name": self.name,
            "skill_path": self.skill_path,
            "query_received": query,
            "simulated_output": f"Skill '{self.name}' successfully activated for goal: {query}",
        }

    @classmethod
    def from_skill_file(cls, skill_md_path: str | Path) -> AgentSkillConnector | None:
        """Parses a SKILL.md file and creates an AgentSkillConnector."""
        p = Path(skill_md_path)
        if not p.exists() or not p.is_file():
            return None

        content = p.read_text(encoding="utf-8", errors="ignore")
        # Match YAML frontmatter between --- and ---
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if not fm_match:
            # Fallback if no frontmatter
            name = p.parent.name
            desc = content[:200].replace("\n", " ")
            return cls(skill_id=name, name=name, description=desc, skill_path=str(p))

        frontmatter_str = fm_match.group(1)
        body = fm_match.group(2)
        try:
            meta = yaml.safe_load(frontmatter_str) or {}
        except yaml.YAMLError:
            meta = {}

        skill_id = meta.get("name") or p.parent.name
        name = meta.get("name") or skill_id.replace("-", " ").title()
        desc = meta.get("description") or (body[:200].replace("\n", " ") if body else "Antigravity Agent Skill")

        # Keywords from triggers or name
        kw = meta.get("triggers", [])
        if isinstance(kw, list):
            kw = [str(k) for k in kw]
        else:
            kw = []

        return cls(
            skill_id=skill_id,
            name=name,
            description=desc,
            skill_path=str(p),
            keywords=kw,
        )

    @classmethod
    def scan_skills_directory(cls, base_dir: str | Path) -> list[AgentSkillConnector]:
        """Scans a directory for all SKILL.md files and converts them to connectors."""
        connectors: list[AgentSkillConnector] = []
        root = Path(base_dir)
        if not root.exists() or not root.is_dir():
            return connectors

        for skill_file in root.glob("**/SKILL.md"):
            conn = cls.from_skill_file(skill_file)
            if conn:
                connectors.append(conn)
        return connectors
