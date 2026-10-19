"""
RAG + CAG + MAG Regulatory Memory Triad Engine (2027 Next-Gen Architecture).
Combines:
1. CAG (Cache-Augmented Generation): Full-document context pinning with zero-latency O(1) lookups.
2. RAG (Retrieval-Augmented Generation): Hybrid keyword & semantic relevance ranking.
3. MAG (Memory-Augmented Graph): Directed NetworkX knowledge graph mapping articles to system controls.
"""

from __future__ import annotations

import re
from typing import Any, ClassVar

import networkx as nx
from pydantic import BaseModel, Field

from .pdf_ingestion import IngestedRegulatoryDocument, RegulatoryArticle


# ==========================================
# 1. CAG: CACHE-AUGMENTED GENERATION STORE
# ==========================================
class CAGStore:
    """
    Cache-Augmented Generation In-Memory Pinned Context.
    Avoids chunk boundary loss by pinning the complete regulatory document
    in structured RAM for instant O(1) article and topic access.
    """

    def __init__(self, doc: IngestedRegulatoryDocument):
        self.doc = doc
        self.pinned_articles: dict[str, RegulatoryArticle] = dict(doc.articles)
        self.topic_index: dict[str, list[str]] = {}
        self._build_topic_index()

    def _build_topic_index(self) -> None:
        """Indexes articles by detected compliance domains."""
        for art_id, art in self.pinned_articles.items():
            for kw in art.keywords:
                if kw not in self.topic_index:
                    self.topic_index[kw] = []
                self.topic_index[kw].append(art_id)

    def get_article(self, article_id: str) -> RegulatoryArticle | None:
        """Instant O(1) retrieval of full article context."""
        return self.pinned_articles.get(article_id)

    def get_by_topic(self, topic_keyword: str) -> list[RegulatoryArticle]:
        """Retrieves all articles relevant to a compliance domain."""
        art_ids = self.topic_index.get(topic_keyword.lower(), [])
        return [self.pinned_articles[aid] for aid in art_ids if aid in self.pinned_articles]

    def get_all_mandates(self) -> list[tuple[str, str, int]]:
        """Returns list of (article_id, mandate_text, page_number)."""
        res = []
        for aid, art in self.pinned_articles.items():
            for m in art.mandates:
                res.append((aid, m, art.page_number))
        return res


# ==========================================
# 2. RAG: HYBRID REGULATORY RETRIEVAL
# ==========================================
class RAGSearchResult(BaseModel):
    """Ranked passage retrieved from the active Ground Truth PDF."""
    article_id: str
    article_title: str
    page_number: int
    relevance_score: float
    snippet: str
    matched_terms: list[str] = Field(default_factory=list)


class RAGSearcher:
    """Hybrid keyword and semantic relevance ranking engine."""

    def __init__(self, cag_store: CAGStore):
        self.cag = cag_store

    def search(self, query: str, top_k: int = 5) -> list[RAGSearchResult]:
        """Searches across pinned articles and mandates, returning ranked results."""
        query_terms = [t.lower() for t in re.findall(r"\w+", query) if len(t) >= 3]
        if not query_terms:
            return []

        results: list[RAGSearchResult] = []

        for art_id, art in self.cag.pinned_articles.items():
            content_lower = art.full_text.lower()
            matched = [term for term in query_terms if term in content_lower]
            if not matched:
                continue

            # Calculate frequency and coverage score
            score = 0.0
            for term in matched:
                count = content_lower.count(term)
                score += (count * 1.5)
            # Bonus for matching title
            title_lower = art.title.lower()
            for term in query_terms:
                if term in title_lower:
                    score += 5.0

            # Generate snippet around first match
            first_idx = content_lower.find(matched[0])
            start = max(0, first_idx - 60)
            end = min(len(art.full_text), first_idx + 180)
            snippet = ("..." if start > 0 else "") + art.full_text[start:end].strip() + ("..." if end < len(art.full_text) else "")

            results.append(RAGSearchResult(
                article_id=art_id,
                article_title=art.title,
                page_number=art.page_number,
                relevance_score=round(score, 2),
                snippet=snippet,
                matched_terms=matched,
            ))

        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:top_k]


# ==========================================
# 3. MAG: MEMORY-AUGMENTED GRAPH
# ==========================================
class MAGGraph:
    """
    Memory-Augmented Graph (Knowledge Graph).
    Constructs a directed graph linking Norms -> Articles -> Mandates -> System Controls.
    """

    # Mapping keywords to system control fields
    CONTROL_MAPPING: ClassVar[dict[str, str]] = {
        "rto": "disaster_recovery_rto_hours",
        "continuidad": "disaster_recovery_rto_hours",
        "recuperación": "disaster_recovery_rto_hours",
        "incidente": "incident_reporting_sla_hours",
        "notificación": "incident_reporting_sla_hours",
        "24 horas": "incident_reporting_sla_hours",
        "cifrado": "encryption_at_rest",
        "aes": "encryption_at_rest",
        "terceros": "third_party_risk_assessed",
        "proveedor": "third_party_risk_assessed",
        "supervisión humana": "human_oversight_active",
        "4 ojos": "human_oversight_active",
        "copia de seguridad": "backup_airgapped",
        "failover": "multiregion_failover_tested",
    }

    def __init__(self, doc: IngestedRegulatoryDocument):
        self.doc = doc
        self.graph = nx.DiGraph()
        self._build_graph()

    def _build_graph(self) -> None:
        """Populates the directed knowledge graph."""
        doc_node = f"DOC:{self.doc.filename}"
        self.graph.add_node(doc_node, type="DOCUMENT", title=self.doc.filename, sha256=self.doc.sha256_hash)

        for art_id, art in self.doc.articles.items():
            art_node = f"ART:{art_id}"
            self.graph.add_node(
                art_node,
                type="ARTICLE",
                id=art_id,
                title=art.title,
                page=art.page_number,
            )
            self.graph.add_edge(doc_node, art_node, relation="CONTAINS")

            # Link Mandates and Controls
            for idx, mandate in enumerate(art.mandates, start=1):
                man_node = f"MAN:{art_id}#m{idx}"
                self.graph.add_node(
                    man_node,
                    type="MANDATE",
                    text=mandate,
                    page=art.page_number,
                )
                self.graph.add_edge(art_node, man_node, relation="ENFORCES")

                # Detect if mandate targets a system control
                mandate_lower = mandate.lower()
                for kw, ctrl_field in self.CONTROL_MAPPING.items():
                    if kw in mandate_lower:
                        ctrl_node = f"CTRL:{ctrl_field}"
                        if not self.graph.has_node(ctrl_node):
                            self.graph.add_node(ctrl_node, type="SYSTEM_CONTROL", field=ctrl_field)
                        self.graph.add_edge(man_node, ctrl_node, relation="VALIDATES")

    def get_summary(self) -> dict[str, Any]:
        """Provides graph topology metrics."""
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "articles_count": sum(1 for _, d in self.graph.nodes(data=True) if d.get("type") == "ARTICLE"),
            "mandates_count": sum(1 for _, d in self.graph.nodes(data=True) if d.get("type") == "MANDATE"),
            "controls_mapped": sum(1 for _, d in self.graph.nodes(data=True) if d.get("type") == "SYSTEM_CONTROL"),
        }

    def get_serializable_elements(self) -> dict[str, Any]:
        """Exports graph nodes and edges for visual rendering."""
        nodes = []
        for n, data in self.graph.nodes(data=True):
            nodes.append({"id": n, "label": data.get("title", n), "type": data.get("type", "NODE")})
        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({"source": u, "target": v, "relation": data.get("relation", "LINK")})
        return {"nodes": nodes, "edges": edges}


# ==========================================
# 4. UNIFIED TRIAD ORCHESTRATOR
# ==========================================
class RegulatoryMemoryTriad:
    """The 2027 Unified Regulatory Memory Triad combining CAG, RAG, and MAG."""

    def __init__(self, doc: IngestedRegulatoryDocument):
        self.doc = doc
        self.cag = CAGStore(doc)
        self.rag = RAGSearcher(self.cag)
        self.mag = MAGGraph(doc)

    def query(self, prompt: str) -> dict[str, Any]:
        """Holistic multi-dimensional query answering."""
        rag_hits = self.rag.search(prompt, top_k=3)
        graph_summary = self.mag.get_summary()

        return {
            "query": prompt,
            "document": self.doc.filename,
            "sha256": self.doc.sha256_hash,
            "cag_total_articles": self.doc.total_articles,
            "rag_top_matches": [h.model_dump() for h in rag_hits],
            "mag_metrics": graph_summary,
        }
