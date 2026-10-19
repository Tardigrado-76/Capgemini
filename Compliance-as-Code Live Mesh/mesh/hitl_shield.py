"""Regulatory Breach Shield and Human-in-the-Loop Gate.

Intercepts non-compliant deployments and high-risk agent operations, enforcing
mandatory human sign-off and digital architectural signatures before release.
"""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class RegulatoryIncident(BaseModel):
    """Formal compliance breach ticket requiring architectural escalation."""
    incident_id: str
    framework: str
    control_id: str
    severity: str  # CRITICAL, HIGH, MEDIUM
    description: str
    violations: list[str] = Field(default_factory=list)
    status: str = "BLOCKED"  # BLOCKED, AUTHORIZED_OVERRIDE, REMEDIATED, REJECTED
    architect_signature: str = ""
    decision_notes: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: str | None = None


class RegulatoryBreachShield:
    """Manages active regulatory blocks and human oversight for the Live Mesh."""

    def __init__(self):
        self.incidents: dict[str, RegulatoryIncident] = {}

    def intercept_breach(
        self,
        framework: str,
        control_id: str,
        description: str,
        severity: str = "HIGH",
        violations: list[str] | None = None,
    ) -> RegulatoryIncident:
        """Blocks execution and generates a compliance escalation ticket."""
        incident_id = f"REG-INC-{len(self.incidents) + 1:03d}"
        incident = RegulatoryIncident(
            incident_id=incident_id,
            framework=framework,
            control_id=control_id,
            severity=severity,
            description=description,
            violations=violations or [],
        )
        self.incidents[incident_id] = incident
        return incident

    def get_blocked_incidents(self) -> list[RegulatoryIncident]:
        """Returns all currently blocking incidents."""
        return [i for i in self.incidents.values() if i.status == "BLOCKED"]

    def authorize_override(self, incident_id: str, architect_signature: str, notes: str) -> bool:
        """Grants an explicit human authorization override for the exception."""
        if incident_id in self.incidents:
            inc = self.incidents[incident_id]
            inc.status = "AUTHORIZED_OVERRIDE"
            inc.architect_signature = architect_signature
            inc.decision_notes = notes
            inc.resolved_at = datetime.now(timezone.utc).isoformat()
            return True
        return False

    def remediate_incident(self, incident_id: str, notes: str) -> bool:
        """Marks the incident as remediated after successful code fix."""
        if incident_id in self.incidents:
            inc = self.incidents[incident_id]
            inc.status = "REMEDIATED"
            inc.decision_notes = notes
            inc.resolved_at = datetime.now(timezone.utc).isoformat()
            return True
        return False
