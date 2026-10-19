"""Semantic Discovery Protocol (SDP) - Core Specification Package.
Standardizes progressive capability disclosure and intent routing for AI agents.
"""

from .progressive_hydrator import ProgressiveHydrator
from .registry import CapabilityRegistry
from .semantic_router import SemanticRouter
from .spec import (
    CapabilitySummary,
    CapabilityTier,
    CapabilityType,
    HydratedSchema,
    RoutingMatch,
    RoutingQuery,
    ValidationVerdict,
)
from .validator import MultiLevelValidator

__all__ = [
    "CapabilityRegistry",
    "CapabilitySummary",
    "CapabilityTier",
    "CapabilityType",
    "HydratedSchema",
    "MultiLevelValidator",
    "ProgressiveHydrator",
    "RoutingMatch",
    "RoutingQuery",
    "SemanticRouter",
    "ValidationVerdict",
]
