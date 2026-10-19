"""Semantic Intent Router Engine.

Implements hybrid lexical and semantic similarity matching to map natural language
agent intentions into ranked Top-K capability candidates (Tier 1).
"""

import re
import unicodedata

from .registry import CapabilityRegistry
from .spec import CapabilitySummary, RoutingMatch, RoutingQuery


class SemanticRouter:
    """Routes agent intent queries to the most relevant capabilities."""

    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry

    def route(self, query: RoutingQuery) -> list[RoutingMatch]:
        """Performs hybrid semantic ranking across registered capabilities."""
        tokens = self._tokenize(query.query)
        matches: list[RoutingMatch] = []

        all_summaries = self.registry.get_index(
            filter_type=query.filter_type,
            filter_protocol=query.filter_protocol,
        )

        for summary in all_summaries:
            score, reasons = self._calculate_similarity(summary, tokens, query.query)
            if score >= query.min_confidence:
                matches.append(RoutingMatch(
                    capability_id=summary.id,
                    name=summary.name,
                    type=summary.type,
                    confidence=round(score, 3),
                    summary=summary.description,
                    match_reasons=reasons,
                    estimated_tokens=summary.estimated_tokens,
                ))

        # Sort descending by confidence score
        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches[:query.top_k]

    def _normalize(self, text: str) -> str:
        """Removes diacritics/accents and converts to lowercase."""
        nfkd = unicodedata.normalize("NFKD", text)
        return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()

    def _tokenize(self, text: str) -> set[str]:
        """Extracts normalized alphanumeric word tokens."""
        clean = self._normalize(text)
        words = re.findall(r"\b[a-z0-9_-]{3,}\b", clean)
        return set(words)

    def _calculate_similarity(
        self,
        summary: CapabilitySummary,
        query_tokens: set[str],
        raw_query: str,
    ) -> tuple[float, list[str]]:
        """Calculates multi-factor semantic confidence score."""
        reasons = []
        score = 0.0
        normalized_raw = self._normalize(raw_query)

        # Factor 1: Keyword matching (with prefix/stem support)
        matched_keywords = set()
        for kw in summary.keywords:
            norm_kw = self._normalize(kw)
            if norm_kw in query_tokens or any(q_tok.startswith(norm_kw) or norm_kw.startswith(q_tok) for q_tok in query_tokens if len(q_tok) >= 4):
                matched_keywords.add(kw)

        if matched_keywords:
            weight = min(1.0, len(matched_keywords) / max(1, len(summary.keywords) * 0.4))
            score += 0.50 * weight
            reasons.append(f"Keyword matches: {', '.join(sorted(matched_keywords))}")

        # Factor 2: Description token overlap
        desc_tokens = self._tokenize(summary.description)
        desc_hits = set()
        for q_tok in query_tokens:
            for d_tok in desc_tokens:
                if q_tok == d_tok or (len(q_tok) >= 4 and (q_tok.startswith(d_tok) or d_tok.startswith(q_tok))):
                    desc_hits.add(d_tok)

        if desc_hits:
            score += 0.25 * min(1.0, len(desc_hits) / max(1, len(desc_tokens) * 0.25))
            reasons.append(f"Description relevance: {', '.join(sorted(desc_hits))}")

        # Factor 3: Name and ID matching
        name_tokens = self._tokenize(summary.name + " " + summary.id)
        name_hits = query_tokens.intersection(name_tokens)
        if name_hits:
            score += 0.25
            reasons.append(f"Name/ID affinity: {', '.join(sorted(name_hits))}")

        # Direct phrase matching boost
        norm_name = self._normalize(summary.name)
        if norm_name in normalized_raw or any(self._normalize(k) in normalized_raw for k in summary.keywords):
            score = min(1.0, score + 0.15)

        return min(1.0, score), reasons
