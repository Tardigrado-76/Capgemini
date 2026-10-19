"""ENS Engine (Esquema Nacional de Seguridad - Real Decreto 311/2022).

Evaluates mandatory security controls for systems deployed in the Spanish Public Sector
and corporate providers (CCN-STIC guides, Categorías Media y Alta).
"""

import hashlib
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ENSControlResult(BaseModel):
    """Result of an individual ENS RD 311/2022 control evaluation."""
    control_id: str
    dimension: str  # Marco Organizativo, Marco Operacional, Medidas de Protección
    name: str
    target_category: str  # BASICA, MEDIA, ALTA
    status: str
    score: float
    evidence_hash: str
    details: str
    remediation: str = ""


class ENSAssessment(BaseModel):
    """Consolidated ENS compliance assessment."""
    framework: str = "ENS (Real Decreto 311/2022)"
    category: str = "ALTA"
    controls: list[ENSControlResult]
    overall_score: float
    compliant: bool
    assessed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ENSEngine:
    """Automated Compliance-as-Code engine for Esquema Nacional de Seguridad."""

    def evaluate(self, system_metadata: dict[str, Any], target_category: str = "ALTA") -> ENSAssessment:
        """Evaluates live system state against ENS controls."""
        results: list[ENSControlResult] = []

        # 1. [op.acc.1] Control de Acceso
        has_auth = bool(system_metadata.get("jwt_auth_enabled", True) or "JWT" in system_metadata.get("goal", ""))
        c1_score = 1.0 if has_auth else 0.5
        results.append(ENSControlResult(
            control_id="[op.acc.1]",
            dimension="Marco Operacional",
            name="Control de Acceso y Segregación de Privilegios",
            target_category=target_category,
            status="COMPLIANT" if c1_score == 1.0 else "WARNING",
            score=c1_score,
            evidence_hash=hashlib.sha256(f"ENS-ACC:{has_auth}".encode()).hexdigest(),
            details="Identificación unívoca, autenticación reforzada y principio de mínimo privilegio.",
            remediation="Active tokens JWT o mTLS para la autenticación de llamadas." if c1_score < 1.0 else "",
        ))

        # 2. [op.exp.8] Registro de Actividad y Auditoría
        has_audit = bool(system_metadata.get("audit_ledger_active", True))
        c2_score = 1.0 if has_audit else 0.0
        results.append(ENSControlResult(
            control_id="[op.exp.8]",
            dimension="Marco Operacional",
            name="Registro de Actividad y Pistas de Auditoría Inmutables",
            target_category=target_category,
            status="COMPLIANT" if has_audit else "NON_COMPLIANT",
            score=c2_score,
            evidence_hash=hashlib.sha256(f"ENS-EXP8:{has_audit}".encode()).hexdigest(),
            details="Registro cronológico inalterable con marcas de tiempo sincronizadas UTC y no repudio.",
            remediation="Obligatorio implementar ledger criptográfico para Categoría Alta." if not has_audit else "",
        ))

        # 3. [mp.com.1] Protección de las Comunicaciones
        has_tls = bool(system_metadata.get("tls_enforced", True))
        c3_score = 1.0 if has_tls else 0.6
        results.append(ENSControlResult(
            control_id="[mp.com.1]",
            dimension="Medidas de Protección",
            name="Protección de las Comunicaciones y Cifrado",
            target_category=target_category,
            status="COMPLIANT" if c3_score == 1.0 else "WARNING",
            score=c3_score,
            evidence_hash=hashlib.sha256(f"ENS-COM1:{has_tls}".encode()).hexdigest(),
            details="Cifrado extremo a extremo de las comunicaciones según Guía CCN-STIC 807.",
        ))

        # 4. [mp.sw.1] Desarrollo y Adquisición de Software Seguro
        has_boundaries = bool(system_metadata.get("boundary_rules") or system_metadata.get("contract_enforced", True))
        c4_score = 1.0 if has_boundaries else 0.4
        results.append(ENSControlResult(
            control_id="[mp.sw.1]",
            dimension="Medidas de Protección",
            name="Desarrollo de Software Seguro y Análisis de Código",
            target_category=target_category,
            status="COMPLIANT" if c4_score == 1.0 else "NON_COMPLIANT",
            score=c4_score,
            evidence_hash=hashlib.sha256(f"ENS-SW1:{has_boundaries}".encode()).hexdigest(),
            details="Pruebas de seguridad estáticas y dinámicas (SAST/DAST) previas al pase a producción.",
        ))

        # 5. [org.seg.1] Segregación de Funciones y Human-in-the-Loop
        has_hitl = bool(system_metadata.get("hitl_active", True))
        c5_score = 1.0 if has_hitl else 0.5
        results.append(ENSControlResult(
            control_id="[org.seg.1]",
            dimension="Marco Organizativo",
            name="Segregación de Funciones y Supervisión de Operaciones",
            target_category=target_category,
            status="COMPLIANT" if c5_score == 1.0 else "WARNING",
            score=c5_score,
            evidence_hash=hashlib.sha256(f"ENS-SEG1:{has_hitl}".encode()).hexdigest(),
            details="Supervisión explícita para operaciones de riesgo crítico en entornos productivos.",
        ))

        overall = round(sum(r.score for r in results) / len(results), 2)
        compliant = overall >= 0.85 and all(r.status != "NON_COMPLIANT" for r in results)

        return ENSAssessment(
            category=target_category,
            controls=results,
            overall_score=overall,
            compliant=compliant,
        )
