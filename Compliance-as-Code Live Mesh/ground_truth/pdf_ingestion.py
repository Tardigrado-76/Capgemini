"""
PDF Ingestion & Structural Clause Extraction for Regulatory Ground Truth.
Converts arbitrary regulatory PDFs (DORA, NIS2, ENS, internal policies) into
structured, hash-verified normative knowledge for the RAG/CAG/MAG memory triad.
"""

from __future__ import annotations

import hashlib
import io
import re
import uuid
from datetime import datetime, timezone
from typing import ClassVar

from pydantic import BaseModel, Field
from pypdf import PdfReader


def compute_bytes_sha256(data: bytes) -> str:
    """Computes SHA-256 hash of raw byte payload."""
    return hashlib.sha256(data).hexdigest()


class RegulatoryArticle(BaseModel):
    """Structured representation of a normative article or clause."""
    article_id: str  # e.g., "Art. 11", "Art. 28", "Sección 4.2"
    title: str
    page_number: int
    full_text: str
    mandates: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)


class IngestedRegulatoryDocument(BaseModel):
    """Complete ingested document serving as the active 'Fuente de Verdad'."""
    doc_id: str = Field(default_factory=lambda: f"doc_{uuid.uuid4().hex[:12]}")
    filename: str
    sha256_hash: str
    total_pages: int
    articles: dict[str, RegulatoryArticle] = Field(default_factory=dict)
    raw_text: str
    ingested_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def total_articles(self) -> int:
        return len(self.articles)

    @property
    def total_mandates(self) -> int:
        return sum(len(a.mandates) for a in self.articles.values())


class PDFIngestionService:
    """Extracts, parses, and structures regulatory PDF documentation."""

    IMPERATIVE_PATTERNS: ClassVar[list[re.Pattern[str]]] = [
        re.compile(r"([^.!?\n]+(?:deberá|deberán|garantizará|garantizarán|obligatorio|exigirá|establecerá|shall|must|ensure)[^.!?\n]+[.!?])", re.IGNORECASE),
        re.compile(r"([^.!?\n]+(?:plazo máximo|tiempo de recuperación|RTO|RPO|24 horas|72 horas|cifrado|auditoría|4 ojos)[^.!?\n]+[.!?])", re.IGNORECASE),
    ]

    ARTICLE_HEADER_PATTERN = re.compile(
        r"(?:Artículo|Art\.|Article|Sección|Section)\s+([0-9]+[a-zA-Z]?(?:\.[0-9]+)?)\s*[:.\-–]?\s*([^\n]+)?",
        re.IGNORECASE,
    )

    KEYWORD_REGISTRY: ClassVar[list[str]] = [
        "resiliencia", "dora", "nis2", "continuidad", "rto", "rpo", "ciberseguridad",
        "incidente", "notificación", "csirt", "copia de seguridad", "cifrado", "aes",
        "terceros", "proveedor", "sla", "auditoría", "4 ojos", "supervisión humana",
        "riesgo", "vulnerabilidad", "failover", "alta disponibilidad", "ens", "gdpr"
    ]

    @classmethod
    def ingest_pdf(
        cls,
        source: str | bytes,
        filename: str | None = None,
    ) -> IngestedRegulatoryDocument:
        """
        Parses a PDF from a filesystem path or raw bytes, extracting articles,
        mandates, and computing its cryptographic SHA-256 fingerprint.
        """
        if isinstance(source, str):
            with open(source, "rb") as f:
                pdf_bytes = f.read()
            doc_name = filename or source.split("/")[-1].split("\\")[-1]
        else:
            pdf_bytes = source
            doc_name = filename or "documento_normativo.pdf"

        sha256_hash = compute_bytes_sha256(pdf_bytes)
        reader = PdfReader(io.BytesIO(pdf_bytes))
        total_pages = len(reader.pages)

        page_texts: list[str] = []
        raw_full_builder: list[str] = []

        for idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            page_texts.append(text)
            raw_full_builder.append(f"--- [PÁGINA {idx}] ---\n{text}")

        raw_text = "\n\n".join(raw_full_builder)

        # Extract articles by page
        articles: dict[str, RegulatoryArticle] = {}
        current_article_id = "Preámbulo / Disposiciones Iniciales"
        current_title = "Introducción Normativa"
        current_page = 1
        current_buffer: list[str] = []

        for p_num, text in enumerate(page_texts, start=1):
            lines = text.split("\n")
            for line in lines:
                match = cls.ARTICLE_HEADER_PATTERN.search(line)
                if match:
                    # Save previous buffer
                    if current_buffer:
                        full_content = " ".join(current_buffer).strip()
                        if full_content:
                            mandates = cls._extract_mandates(full_content)
                            kws = cls._extract_keywords(full_content)
                            articles[current_article_id] = RegulatoryArticle(
                                article_id=current_article_id,
                                title=current_title,
                                page_number=current_page,
                                full_text=full_content,
                                mandates=mandates,
                                keywords=kws,
                            )
                    # Start new article
                    art_num = match.group(1)
                    raw_title = match.group(2) or "Disposiciones Generales"
                    current_article_id = f"Art. {art_num}"
                    current_title = raw_title.strip()
                    current_page = p_num
                    current_buffer = [line]
                else:
                    current_buffer.append(line)

        # Flush final buffer
        if current_buffer:
            full_content = " ".join(current_buffer).strip()
            if full_content:
                mandates = cls._extract_mandates(full_content)
                kws = cls._extract_keywords(full_content)
                articles[current_article_id] = RegulatoryArticle(
                    article_id=current_article_id,
                    title=current_title,
                    page_number=current_page,
                    full_text=full_content,
                    mandates=mandates,
                    keywords=kws,
                )

        # Fallback if no explicit "Artículo" markers were found (e.g. general security policy)
        if len(articles) <= 1:
            articles = cls._segment_by_pages(page_texts)

        return IngestedRegulatoryDocument(
            filename=doc_name,
            sha256_hash=sha256_hash,
            total_pages=total_pages,
            articles=articles,
            raw_text=raw_text,
        )

    @classmethod
    def _extract_mandates(cls, text: str) -> list[str]:
        """Extracts enforceable normative sentences containing legal imperatives."""
        found = set()
        for pat in cls.IMPERATIVE_PATTERNS:
            for match in pat.finditer(text):
                cleaned = match.group(1).strip()
                if len(cleaned) > 20:
                    found.add(cleaned)
        return sorted(found)

    @classmethod
    def _extract_keywords(cls, text: str) -> list[str]:
        """Detects relevant compliance keywords present in the text."""
        lower = text.lower()
        return [kw for kw in cls.KEYWORD_REGISTRY if kw in lower]

    @classmethod
    def _segment_by_pages(cls, page_texts: list[str]) -> dict[str, RegulatoryArticle]:
        """Fallback segmentation by document page when explicit article headings are absent."""
        articles = {}
        for p_idx, text in enumerate(page_texts, start=1):
            if not text.strip():
                continue
            art_id = f"Sección Pág. {p_idx}"
            mandates = cls._extract_mandates(text)
            kws = cls._extract_keywords(text)
            articles[art_id] = RegulatoryArticle(
                article_id=art_id,
                title=f"Cláusulas y Requerimientos de Página {p_idx}",
                page_number=p_idx,
                full_text=text.strip(),
                mandates=mandates,
                keywords=kws,
            )
        return articles
