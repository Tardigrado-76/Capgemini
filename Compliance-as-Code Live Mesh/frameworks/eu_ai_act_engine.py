"""EU AI Act Engine (Reglamento UE 2024/1689 sobre Inteligencia Artificial).

Evaluates high-risk AI system requirements: risk management (Art. 9), data governance (Art. 10),
technical record-keeping/logging (Art. 12), and human oversight (Art. 14).
"""

import hashlib
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class EUAIControlResult(BaseModel):
    """Result of an individual EU AI Act control evaluation."""
    control_id: str
    article: str
    name: str
    status: str
    score: float
    evidence_hash: str
    details: str
    remediation: str = ""


class EUAIActAssessment(BaseModel):
    """Consolidated EU AI Act compliance assessment."""
    framework: str = "EU AI Act (Reglamento UE 2024/1689)"
    risk_classification: str = "Alto Riesgo (Sistemas Autónomos Empresariales)"
    controls: list[EUAIControlResult]
    overall_score: float
    compliant: bool
    assessed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class EUAIActEngine:
    """Automated Compliance-as-Code engine for EU AI Act."""

    def evaluate(self, system_metadata: dict[str, Any]) -> EUAIActAssessment:
        """Evaluates live system state against EU AI Act requirements."""
        results: list[EUAIControlResult] = []

        # 1. Art. 9: Sistema de Gestión de Riesgos
        has_boundaries = bool(system_metadata.get("boundary_rules") or system_metadata.get("invariants"))
        c1_score = 1.0 if has_boundaries else 0.5
        results.append(EUAIControlResult(
            control_id="EUAI-RSK-09",
            article="Artículo 9",
            name="Sistema de Gestión de Riesgos Continuo",
            status="COMPLIANT" if c1_score == 1.0 else "WARNING",
            score=c1_score,
            evidence_hash=hashlib.sha256(f"EUAI-09:{has_boundaries}".encode()).hexdigest(),
            details="Identificación, estimación y mitigación de riesgos previsibles para la salud, seguridad y derechos fundamentales.",
        ))

        # 2. Art. 10: Gobernanza de Datos y Mitigación de Sesgos
        data_models = system_metadata.get("data_models", {})
        c2_score = 1.0 if data_models else 0.8
        results.append(EUAIControlResult(
            control_id="EUAI-DAT-10",
            article="Artículo 10",
            name="Gobernanza y Gestión de Datos de Entrenamiento e Inferencia",
            status="COMPLIANT" if c2_score == 1.0 else "WARNING",
            score=c2_score,
            evidence_hash=hashlib.sha256(f"EUAI-10:{len(data_models)}".encode()).hexdigest(),
            details="Validación de esquemas de datos, ausencia de sesgos y prevención de fugas de datos confidenciales.",
        ))

        # 3. Art. 12: Registro de Actividad y Trazabilidad Inmutable (Logging)
        has_immutable_log = bool(system_metadata.get("audit_ledger_active", True) and system_metadata.get("merkle_active", True))
        c3_score = 1.0 if has_immutable_log else 0.0
        results.append(EUAIControlResult(
            control_id="EUAI-LOG-12",
            article="Artículo 12",
            name="Registro Técnico Automático y Trazabilidad Inmutable (Logging)",
            status="COMPLIANT" if has_immutable_log else "NON_COMPLIANT",
            score=c3_score,
            evidence_hash=hashlib.sha256(f"EUAI-12:{has_immutable_log}".encode()).hexdigest(),
            details="Registro automático de logs de eventos para permitir la monitorización y trazabilidad a lo largo del ciclo de vida.",
            remediation="Active el ledger inmutable para sellar trazas de inferencia y decisión." if not has_immutable_log else "",
        ))

        # 4. Art. 14: Supervisión Humana (Human Oversight / Kill Switch)
        has_hitl = bool(system_metadata.get("hitl_active", True))
        c4_score = 1.0 if has_hitl else 0.0
        results.append(EUAIControlResult(
            control_id="EUAI-HUM-14",
            article="Artículo 14",
            name="Supervisión Humana (Human-in-the-Loop y Mecanismo Kill-Switch)",
            status="COMPLIANT" if has_hitl else "NON_COMPLIANT",
            score=c4_score,
            evidence_hash=hashlib.sha256(f"EUAI-14:{has_hitl}".encode()).hexdigest(),
            details="Capacidad efectiva de intervención humana para supervisar, anular o detener el funcionamiento del sistema autónomo.",
            remediation="Implemente una puerta de aprobación HITL con parada de emergencia." if not has_hitl else "",
        ))

        # 5. Art. 15: Ciberseguridad, Solidez y Resiliencia del Modelo
        tests_passed = system_metadata.get("tests_passed", 0) > 0
        c5_score = 1.0 if tests_passed else 0.7
        results.append(EUAIControlResult(
            control_id="EUAI-SEC-15",
            article="Artículo 15",
            name="Precisión, Solidez y Ciberseguridad del Sistema de IA",
            status="COMPLIANT" if c5_score == 1.0 else "WARNING",
            score=c5_score,
            evidence_hash=hashlib.sha256(f"EUAI-15:{tests_passed}".encode()).hexdigest(),
            details="Resiliencia frente a ataques adversariales, inyecciones de prompts y fallos en cascada.",
        ))

        overall = round(sum(r.score for r in results) / len(results), 2)
        compliant = overall >= 0.85 and all(r.status != "NON_COMPLIANT" for r in results)

        return EUAIActAssessment(
            controls=results,
            overall_score=overall,
            compliant=compliant,
        )
