"""Human-in-the-Loop (HITL) Approval Gate.

Provides strict architectural oversight when agents encounter boundary violations,
max evaluation retry thresholds, or request exceptional architectural deviations.
"""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class HITLTicket(BaseModel):
    """Pending architectural decision ticket for human sign-off."""
    ticket_id: str
    contract_id: str
    target_file: str
    severity: str  # CRITICAL, HIGH, MEDIUM
    reason: str
    violations: list[str] = Field(default_factory=list)
    proposed_diff: str = ""
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED, AMENDED
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    decision_notes: str = ""
    decided_at: str | None = None


class HITLApprovalGate:
    """Manages Human-in-the-Loop approval workflows for White Coding."""

    def __init__(self):
        self.tickets: dict[str, HITLTicket] = {}

    def raise_ticket(
        self,
        contract_id: str,
        target_file: str,
        reason: str,
        severity: str = "HIGH",
        violations: list[str] | None = None,
        proposed_diff: str = "",
    ) -> HITLTicket:
        """Creates a pending review ticket for the human architect."""
        ticket_id = f"HITL-{len(self.tickets) + 1:03d}"
        ticket = HITLTicket(
            ticket_id=ticket_id,
            contract_id=contract_id,
            target_file=target_file,
            severity=severity,
            reason=reason,
            violations=violations or [],
            proposed_diff=proposed_diff,
        )
        self.tickets[ticket_id] = ticket
        return ticket

    def get_pending_tickets(self) -> list[HITLTicket]:
        """Returns all open tickets awaiting human decision."""
        return [t for t in self.tickets.values() if t.status == "PENDING"]

    def approve(self, ticket_id: str, notes: str = "Approved by Architect") -> bool:
        """Approves the exception or deviation."""
        if ticket_id in self.tickets:
            self.tickets[ticket_id].status = "APPROVED"
            self.tickets[ticket_id].decision_notes = notes
            self.tickets[ticket_id].decided_at = datetime.now(timezone.utc).isoformat()
            return True
        return False

    def reject(self, ticket_id: str, notes: str = "Rejected by Architect") -> bool:
        """Rejects the proposal, halting or rolling back changes."""
        if ticket_id in self.tickets:
            self.tickets[ticket_id].status = "REJECTED"
            self.tickets[ticket_id].decision_notes = notes
            self.tickets[ticket_id].decided_at = datetime.now(timezone.utc).isoformat()
            return True
        return False
