"""Tests for Token Efficiency Benchmark Suite."""

from benchmark.token_comparator import TokenBenchmarkSuite


def test_token_benchmark_savings():
    suite = TokenBenchmarkSuite()
    res = suite.compare(catalog_size=50, selected_tools_count=2)

    assert res.tool_catalog_size == 50
    assert res.naive_stuffing_tokens == 50 * 750  # 37,500 tokens
    assert res.sdp_progressive_tokens < 2_000     # ~1,640 tokens
    assert res.percentage_savings >= 90.0         # Proves >90% context reduction
    assert res.tokens_saved > 35_000
    assert res.monthly_savings_usd > 5.0
