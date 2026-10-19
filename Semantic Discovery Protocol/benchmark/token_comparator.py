"""Token Efficiency & Cost Comparison Benchmark Engine.

Quantifies mathematical token savings and latency reduction between Naive Tool Stuffing
and the Semantic Discovery Protocol (SDP) across enterprise agent workloads.
"""

from pydantic import BaseModel, Field


class BenchmarkComparisonResult(BaseModel):
    """Result of a head-to-head token and cost comparison."""
    tool_catalog_size: int
    selected_tools_count: int
    naive_stuffing_tokens: int
    sdp_progressive_tokens: int
    tokens_saved: int
    percentage_savings: float
    estimated_latency_naive_ms: float
    estimated_latency_sdp_ms: float
    monthly_savings_usd: float  # Based on 100k requests/month at standard pricing
    details: dict[str, int] = Field(default_factory=dict)


class TokenBenchmarkSuite:
    """Simulates and measures context efficiency across scaling catalog sizes."""

    AVG_FULL_SCHEMA_TOKENS = 750    # Average tokens for full JSON Schema + documentation
    AVG_TIER0_SUMMARY_TOKENS = 18   # Tier 0 index footprint per capability
    AVG_HYDRATED_SCHEMA_TOKENS = 350 # Tier 2 standard hydrated schema footprint
    PRICE_PER_MILLION_TOKENS = 3.00  # Enterprise LLM input cost benchmark (USD)

    def compare(
        self,
        catalog_size: int = 50,
        selected_tools_count: int = 2,
        monthly_requests: int = 100_000,
    ) -> BenchmarkComparisonResult:
        """Executes a comparative benchmark across catalog parameters."""
        # 1. Naive Tool-Stuffing: All schemas loaded into every prompt turn
        naive_tokens = catalog_size * self.AVG_FULL_SCHEMA_TOKENS

        # 2. SDP Progressive Disclosure:
        # - Tier 0 index for discovery: catalog_size * 18 tokens
        # - Tier 2 JIT hydration: selected_tools_count * 350 tokens
        # - Tier 1 routing query overhead: ~40 tokens
        tier0_cost = catalog_size * self.AVG_TIER0_SUMMARY_TOKENS
        tier2_cost = selected_tools_count * self.AVG_HYDRATED_SCHEMA_TOKENS
        sdp_tokens = tier0_cost + tier2_cost + 40

        saved_tokens = max(0, naive_tokens - sdp_tokens)
        pct_savings = round((saved_tokens / naive_tokens) * 100, 2) if naive_tokens > 0 else 0.0

        # Latency estimates: ~1.2ms per 100 tokens of prompt evaluation
        latency_naive = round(naive_tokens * 0.012, 1)
        latency_sdp = round(sdp_tokens * 0.012, 1)

        # Monthly savings in USD
        monthly_saved_tokens = saved_tokens * monthly_requests
        monthly_usd = round((monthly_saved_tokens / 1_000_000) * self.PRICE_PER_MILLION_TOKENS, 2)

        return BenchmarkComparisonResult(
            tool_catalog_size=catalog_size,
            selected_tools_count=selected_tools_count,
            naive_stuffing_tokens=naive_tokens,
            sdp_progressive_tokens=sdp_tokens,
            tokens_saved=saved_tokens,
            percentage_savings=pct_savings,
            estimated_latency_naive_ms=latency_naive,
            estimated_latency_sdp_ms=latency_sdp,
            monthly_savings_usd=monthly_usd,
            details={
                "tier0_index_tokens": tier0_cost,
                "tier2_hydrated_tokens": tier2_cost,
                "full_schema_per_tool": self.AVG_FULL_SCHEMA_TOKENS,
            },
        )
