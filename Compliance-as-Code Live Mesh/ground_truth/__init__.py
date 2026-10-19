"""
Ground Truth Regulatory Intelligence Package (RAG + CAG + MAG).
Enables ingesting arbitrary regulatory PDFs (DORA, NIS2, ENS, etc.) as the authoritative
cryptographic 'Fuente de Verdad' for continuous compliance and agent evaluation.
"""

from .ground_truth_evaluator import (
    GroundTruthEvaluationResult,
    GroundTruthEvaluator,
)
from .pdf_ingestion import (
    IngestedRegulatoryDocument,
    PDFIngestionService,
    RegulatoryArticle,
)
from .rag_cag_mag_engine import (
    CAGStore,
    MAGGraph,
    RAGSearcher,
    RegulatoryMemoryTriad,
)

__all__ = [
    "CAGStore",
    "GroundTruthEvaluationResult",
    "GroundTruthEvaluator",
    "IngestedRegulatoryDocument",
    "MAGGraph",
    "PDFIngestionService",
    "RAGSearcher",
    "RegulatoryArticle",
    "RegulatoryMemoryTriad",
]
