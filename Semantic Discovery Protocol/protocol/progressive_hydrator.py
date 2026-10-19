"""Progressive Schema Hydrator Engine.

Implements Just-in-Time (JIT) schema hydration across three granular tiers:
Minimal (~100 tokens), Standard (~350 tokens), and Full (~1,000 tokens).
"""


from .registry import CapabilityRegistry
from .spec import HydratedSchema


class ProgressiveHydrator:
    """Hydrates capability schemas on demand to prevent context-window saturation."""

    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry

    def hydrate(self, capability_id: str, detail_level: str = "standard") -> HydratedSchema | None:
        """Progressively expands the capability schema based on requested detail level."""
        full_spec = self.registry.get_full_spec(capability_id)
        summary = self.registry.get_summary(capability_id)
        if not full_spec or not summary:
            return None

        params = full_spec.get("parameters", {})
        required = full_spec.get("required", [])
        examples = full_spec.get("examples", [])
        docs = full_spec.get("docs", "")

        if detail_level == "minimal":
            # Strip descriptions and examples, only keep types and required
            filtered_params = {
                k: {"type": v.get("type", "string")}
                for k, v in params.items()
            }
            token_estimate = 70 + (len(filtered_params) * 12)
            return HydratedSchema(
                capability_id=capability_id,
                detail_level="minimal",
                parameters_schema=filtered_params,
                required_args=required,
                examples=[],
                documentation="",
                token_cost=token_estimate,
            )

        elif detail_level == "standard":
            # Keep descriptions and defaults, omit verbose documentation
            filtered_params = {
                k: {
                    "type": v.get("type", "string"),
                    "description": v.get("description", ""),
                    "default": v.get("default", None),
                }
                for k, v in params.items()
            }
            token_estimate = 180 + (len(filtered_params) * 35)
            return HydratedSchema(
                capability_id=capability_id,
                detail_level="standard",
                parameters_schema=filtered_params,
                required_args=required,
                examples=examples[:1],
                documentation=docs[:120],
                token_cost=token_estimate,
            )

        else:  # "full"
            token_estimate = 450 + (len(params) * 50) + len(docs.split())
            return HydratedSchema(
                capability_id=capability_id,
                detail_level="full",
                parameters_schema=params,
                required_args=required,
                examples=examples,
                documentation=docs,
                token_cost=token_estimate,
            )
