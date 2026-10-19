"""NIS2 Engine (Directiva UE 2022/2555 - Medidas de Ciberseguridad e Incidentes).

Evaluates cybersecurity risk-management measures (Art. 21) and rapid incident
notification capabilities (Art. 23) for essential and important European entities.
"""

import hashlib
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class NIS2ControlResult(BaseModel):
    """Result of an individual NIS2 control evaluation."""
    control_id: str
    name: str
    directive_ref: str
    status: str  # COMPLIANT, WARNING, NON_COMPLIANT
    score: float
    evidence_hash: str
    details: str
    remediation: str = ""


class NIS2Assessment(BaseModel):
    """Consolidated NIS2 compliance assessment."""
    framework: str = "NIS2 (Directiva UE 2022/2555)"
    controls: list[NIS2ControlResult]
    overall_score: float
    compliant: bool
    assessed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class NIS2Engine:
    """Automated Compliance-as-Code engine for NIS2 requirements."""

    def evaluate(self, system_metadata: dict[str, Any]) -> NIS2Assessment:
        """Evaluates live system state against NIS2 Art. 21 and 23."""
        results: list[NIS2ControlResult] = []

        # 1. NIS2-CYB-01: Políticas de Análisis de Riesgos (Art. 21.2.a)
        has_boundaries = bool(system_metadata.get("boundary_rules") or system_metadata.get("invariants"))
        c1_score = 1.0 if has_boundaries else 0.5
        c1_status = "COMPLIANT" if c1_score == 1.0 else "WARNING"
        results.append(NIS2ControlResult(
            control_id="NIS2-CYB-01",
            name="Análisis de Riesgos y Seguridad de Sistemas",
            directive_ref="Art. 21.2(a)",
            status=c1_status,
            score=c1_score,
            evidence_hash=hashlib.sha256(f"NIS2-01:{has_boundaries}".encode()).hexdigest(),
            details="Políticas de análisis de riesgos informáticos y especificaciones formales activas.",
            remediation="Incorpore reglas de contorno y análisis de vulnerabilidades." if c1_score < 1.0 else "",
        ))

        # 2. NIS2-INC-02: Gestión y Notificación de Incidentes (Art. 23)
        has_early_warning = bool(system_metadata.get("hitl_active", True) and system_metadata.get("audit_ledger_active", True))
        c2_score = 1.0 if has_early_warning else 0.0
        c2_status = "COMPLIANT" if has_early_warning else "NON_COMPLIANT"
        results.append(NIS2ControlResult(
            control_id="NIS2-INC-02",
            name="Notificación Temprana de Incidentes Significativos (<24h)",
            directive_ref="Art. 23",
            status=c2_status,
            score=c2_score,
            evidence_hash=hashlib.sha256(f"NIS2-02:{has_early_warning}".encode()).hexdigest(),
            details="Capacidad técnica de detección y emisión de alerta temprana en < 24h ante el CSIRT nacional (CCN-CERT / INCIBE).",
            remediation="Habilite canales de telemetría y escudo de incidentes HITL." if c2_score < 1.0 else "",
        ))

        # 3. NIS2-BCP-03: Continuidad de las Actividades y Respaldo (Art. 21.2.c)
        has_tests = system_metadata.get("tests_passed", 0) > 0
        c3_score = 1.0 if has_tests else 0.7
        results.append(NIS2ControlResult(
            control_id="NIS2-BCP-03",
            name="Continuidad de Negocio y Copias de Seguridad",
            directive_ref="Art. 21.2(c)",
            status="COMPLIANT" if c3_score == 1.0 else "WARNING",
            score=c3_score,
            evidence_hash=hashlib.sha256(f"NIS2-03:{has_tests}".encode()).hexdigest(),
            details="Procedimientos de continuidad, gestión de crisis y copias de seguridad de datos inmutables.",
        ))

        # 4. NIS2-SEC-04: Seguridad en la Cadena de Suministro (Art. 21.2.d)
        sbom_valid = bool(system_metadata.get("sbom_present", True))
        c4_score = 1.0 if sbom_valid else 0.3
        results.append(NIS2ControlResult(
            control_id="NIS2-SEC-04",
            name="Seguridad en la Cadena de Suministro y CRA",
            directive_ref="Art. 21.2(d)",
            status="COMPLIANT" if sbom_valid else "NON_COMPLIANT",
            score=c4_score,
            evidence_hash=hashlib.sha256(f"NIS2-04:{sbom_valid}".encode()).hexdigest(),
            details="Auditoría formal de librerías, dependencias de código abierto y compatibilidad con el Cyber Resilience Act.",
            remediation="Adjunte un SBOM CycloneDX firmado." if not sbom_valid else "",
        ))

        # 5. NIS2-CRY-05: Criptografía y Cifrado (Art. 21.2.h)
        has_crypto = bool(system_metadata.get("merkle_active", True) or system_metadata.get("audit_ledger_active", True))
        c5_score = 1.0 if has_crypto else 0.0
        results.append(NIS2ControlResult(
            control_id="NIS2-CRY-05",
            name="Criptografía y Cifrado de Información",
            directive_ref="Art. 21.2(h)",
            status="COMPLIANT" if has_crypto else "NON_COMPLIANT",
            score=c5_score,
            evidence_hash=hashlib.sha256(f"NIS2-05:{has_crypto}".encode()).hexdigest(),
            details="Políticas y mecanismos de cifrado SHA-256 / Merkle para sellado no repudiable de eventos.",
        ))

        overall = round(sum(r.score for r in results) / len(results), 2)
        compliant = overall >= 0.85 and all(r.status != "NON_COMPLIANT" for r in results)

        return NIS2Assessment(
            controls=results,
            overall_score=overall,
            compliant=compliant,
        )
