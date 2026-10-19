"""
Unit tests for PDF Ground Truth Ingestion & RAG/CAG/MAG Memory Triad.
"""

import pytest

from ground_truth.ground_truth_evaluator import GroundTruthEvaluator
from ground_truth.pdf_ingestion import PDFIngestionService
from ground_truth.rag_cag_mag_engine import (
    CAGStore,
    MAGGraph,
    RAGSearcher,
    RegulatoryMemoryTriad,
)
from ground_truth.sample_generator import generate_sample_regulatory_pdf


@pytest.fixture(scope="module")
def sample_pdf_path(tmp_path_factory):
    fn = tmp_path_factory.mktemp("normas") / "Normativa_DORA_NIS2_Test.pdf"
    path = generate_sample_regulatory_pdf(str(fn))
    return path


def test_pdf_ingestion(sample_pdf_path):
    doc = PDFIngestionService.ingest_pdf(sample_pdf_path)

    assert doc.total_pages >= 1
    assert len(doc.sha256_hash) == 64
    assert doc.total_articles >= 3
    assert doc.total_mandates >= 4

    # Check extracted article IDs
    article_keys = list(doc.articles.keys())
    assert any("Art. 11" in k for k in article_keys)
    assert any("Art. 19" in k for k in article_keys)
    assert any("Art. 28" in k for k in article_keys)


def test_cag_store(sample_pdf_path):
    doc = PDFIngestionService.ingest_pdf(sample_pdf_path)
    cag = CAGStore(doc)

    art11 = cag.get_article("Art. 11")
    assert art11 is not None
    assert art11.page_number >= 1
    assert len(art11.mandates) > 0

    topic_results = cag.get_by_topic("ciberseguridad")
    assert len(topic_results) >= 1


def test_rag_searcher(sample_pdf_path):
    doc = PDFIngestionService.ingest_pdf(sample_pdf_path)
    cag = CAGStore(doc)
    rag = RAGSearcher(cag)

    hits = rag.search("plazo máximo de 24 horas notificación incidente", top_k=2)
    assert len(hits) >= 1
    top_hit = hits[0]
    assert "Art. 19" in top_hit.article_id or "19" in top_hit.snippet
    assert top_hit.relevance_score > 0


def test_mag_graph_construction(sample_pdf_path):
    doc = PDFIngestionService.ingest_pdf(sample_pdf_path)
    mag = MAGGraph(doc)
    summary = mag.get_summary()

    assert summary["total_nodes"] > 5
    assert summary["total_edges"] > 5
    assert summary["articles_count"] >= 3
    assert summary["controls_mapped"] >= 2


def test_ground_truth_evaluator_compliant_system(sample_pdf_path):
    doc = PDFIngestionService.ingest_pdf(sample_pdf_path)
    triad = RegulatoryMemoryTriad(doc)
    evaluator = GroundTruthEvaluator(triad)

    system_metadata = {
        "system_name": "Bank-Core-Payment-Gateway",
        "disaster_recovery_rto_hours": 1.5,   # <= 2.0 -> PASS
        "incident_reporting_sla_hours": 12.0,  # <= 24.0 -> PASS
        "encryption_at_rest": True,           # True -> PASS
        "third_party_risk_assessed": True,    # True -> PASS
        "human_oversight_active": True,       # True -> PASS
        "multiregion_failover_tested": True,  # True -> PASS
    }

    result = evaluator.evaluate_system(system_metadata)

    assert result.is_compliant is True
    assert result.ground_truth_score == 100.0
    assert result.breached_controls_count == 0
    assert len(result.citations) >= 2
    assert any("Art." in c and "Pág." in c for c in result.citations)


def test_ground_truth_evaluator_breach_detection(sample_pdf_path):
    doc = PDFIngestionService.ingest_pdf(sample_pdf_path)
    triad = RegulatoryMemoryTriad(doc)
    evaluator = GroundTruthEvaluator(triad)

    # Violating RTO (>2h) and SLA (>24h)
    system_metadata = {
        "system_name": "Vulnerable-Legacy-Service",
        "disaster_recovery_rto_hours": 8.0,   # Breaches 2h limit!
        "incident_reporting_sla_hours": 96.0,  # Breaches 24h limit!
        "encryption_at_rest": False,          # Breaches encryption mandate!
    }

    result = evaluator.evaluate_system(system_metadata)

    assert result.is_compliant is False
    assert result.breached_controls_count >= 2
    assert result.ground_truth_score < 70.0
    # Citations must explain exact breach
    breach_verdicts = [v for v in result.verdicts if not v.compliant]
    assert any("excede" in v.explanation.lower() or "incumplimiento" in v.explanation.lower() for v in breach_verdicts)
