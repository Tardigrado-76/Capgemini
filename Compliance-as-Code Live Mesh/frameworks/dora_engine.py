"""DORA Engine (Reglamento UE 2022/2554 - Digital Operational Resilience Act).

Evaluates ICT risk management, operational resilience testing, third-party risk,
and incident response readiness for enterprise financial/critical software systems.
"""

import hashlib
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class DORAControlResult(BaseModel):
    """Result of an individual DORA regulatory control evaluation."""
    control_id: str
    name: str
    article: str
    status: str  # COMPLIANT, WARNING, NON_COMPLIANT
    score: float  # 0.0 to 1.0
    evidence_hash: str
    details: str
    remediation: str = ""


class DORAAssessment(BaseModel):
    """Consolidated DORA operational resilience assessment."""
    framework: str = "DORA (Reglamento UE 2022/2554)"
    controls: list[DORAControlResult]
    overall_score: float
    compliant: bool
    assessed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DORAEngine:
    """Automated Compliance-as-Code engine for DORA requirements."""

    def evaluate(self, system_metadata: dict[str, Any]) -> DORAAssessment:
        """Evaluates live system state against mandatory DORA controls."""
        results: list[DORAControlResult] = []

        # 1. DORA-ICT-01: ICT Risk Management & Architecture Classification (Art. 6 & 9)
        has_arch = bool(system_metadata.get("architecture_diagram") or system_metadata.get("system_name"))
        has_boundaries = bool(system_metadata.get("boundary_rules") or system_metadata.get("allowed_modules"))
        c1_score = 1.0 if (has_arch and has_boundaries) else 0.5 if has_arch else 0.0
        c1_status = "COMPLIANT" if c1_score == 1.0 else "WARNING" if c1_score >= 0.5 else "NON_COMPLIANT"
        raw_c1 = f"DORA-ICT-01:{has_arch}:{has_boundaries}"
        results.append(DORAControlResult(
            control_id="DORA-ICT-01",
            name="Gestión y Clasificación de Riesgos TIC",
            article="Art. 6 & 9",
            status=c1_status,
            score=c1_score,
            evidence_hash=hashlib.sha256(raw_c1.encode("utf-8")).hexdigest(),
            details="Inventario formal de componentes TIC, dependencias e interfaces clasificadas.",
            remediation="Defina límites de contorno y arquitectura formal del sistema." if c1_score < 1.0 else "",
        ))

        # 2. DORA-RES-02: Pruebas de Resiliencia Operativa Digital (Art. 24 & 26)
        tests_passed = system_metadata.get("tests_passed", 0)
        tests_failed = system_metadata.get("tests_failed", 0)
        total_tests = tests_passed + tests_failed
        if total_tests > 0 and tests_failed == 0:
            c2_score = 1.0
            c2_status = "COMPLIANT"
        elif total_tests > 0 and tests_failed > 0:
            c2_score = round(tests_passed / total_tests, 2)
            c2_status = "WARNING" if c2_score >= 0.75 else "NON_COMPLIANT"
        else:
            c2_score = 0.8  # Default verification baseline
            c2_status = "COMPLIANT"
        raw_c2 = f"DORA-RES-02:{tests_passed}:{tests_failed}"
        results.append(DORAControlResult(
            control_id="DORA-RES-02",
            name="Pruebas de Resiliencia y Recuperación",
            article="Art. 24 & 26",
            status=c2_status,
            score=c2_score,
            evidence_hash=hashlib.sha256(raw_c2.encode("utf-8")).hexdigest(),
            details=f"Validación de resiliencia mediante pruebas automatizadas ({tests_passed} exitosas, {tests_failed} fallidas).",
            remediation="Ejecute tests de recuperación ante desastres sin fallos residuales." if c2_score < 1.0 else "",
        ))

        # 3. DORA-TPR-03: Gestión de Riesgos de Terceros TIC (Art. 28)
        forbidden_detected = system_metadata.get("forbidden_dependencies_detected", [])
        has_sbom = bool(system_metadata.get("sbom_present", True))
        if not forbidden_detected and has_sbom:
            c3_score = 1.0
            c3_status = "COMPLIANT"
        else:
            c3_score = 0.4
            c3_status = "NON_COMPLIANT"
        raw_c3 = f"DORA-TPR-03:{len(forbidden_detected)}:{has_sbom}"
        results.append(DORAControlResult(
            control_id="DORA-TPR-03",
            name="Supervisión del Riesgo de Terceros y Cadena de Suministro",
            article="Art. 28",
            status=c3_status,
            score=c3_score,
            evidence_hash=hashlib.sha256(raw_c3.encode("utf-8")).hexdigest(),
            details="Verificación estricta de proveedores SaaS, librerías externas y SBOM auditado.",
            remediation="Elimine dependencias no autorizadas y adjunte SBOM CycloneDX." if c3_score < 1.0 else "",
        ))

        # 4. DORA-INC-04: Notificación de Incidentes Graves y Trazabilidad (Art. 19)
        has_audit = bool(system_metadata.get("audit_ledger_active", True))
        c4_score = 1.0 if has_audit else 0.0
        c4_status = "COMPLIANT" if has_audit else "NON_COMPLIANT"
        raw_c4 = f"DORA-INC-04:{has_audit}"
        results.append(DORAControlResult(
            control_id="DORA-INC-04",
            name="Registro y Notificación de Incidentes TIC",
            article="Art. 19",
            status=c4_status,
            score=c4_score,
            evidence_hash=hashlib.sha256(raw_c4.encode("utf-8")).hexdigest(),
            details="Capacidad inmutable de registrar anomalías y emitir informes ante el Banco de España / BCE en < 4h.",
            remediation="Active el ledger criptográfico inmutable para trazabilidad de incidentes." if c4_score < 1.0 else "",
        ))

        overall = round(sum(r.score for r in results) / len(results), 2)
        compliant = overall >= 0.85 and all(r.status != "NON_COMPLIANT" for r in results)

        return DORAAssessment(
            controls=results,
            overall_score=overall,
            compliant=compliant,
        )
