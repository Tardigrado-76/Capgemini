"""White Coding Harness - Core Architecture Package.
Implements White Coding paradigm by Iwan Rochus van der Kleijn.
"""

from .adversarial_evaluator import AdversarialEvaluator, EvaluationReport
from .bounded_generator import BoundedGenerator
from .contract_locker import ContractLocker, StepContract
from .hitl_gate import HITLApprovalGate, HITLTicket
from .telemetry import TelemetryManager
from .whiteboard_architect import WhiteboardArchitect, WhiteboardSpec

__all__ = [
    "AdversarialEvaluator",
    "BoundedGenerator",
    "ContractLocker",
    "EvaluationReport",
    "HITLApprovalGate",
    "HITLTicket",
    "StepContract",
    "TelemetryManager",
    "WhiteboardArchitect",
    "WhiteboardSpec",
]
