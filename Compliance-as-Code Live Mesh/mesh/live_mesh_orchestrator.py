"""Live Mesh Orchestrator Engine.

Ingests events (Git commits, CI/CD deploys, autonomous agent actions), evaluates them
concurrently across all 4 European regulatory engines, and seals immutable evidence.
"""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from frameworks.cra_sbom_engine import CRASBOMEngine, SBOMValidationResult
from frameworks.dora_engine import DORAAssessment, DORAEngine
from frameworks.ens_engine import ENSAssessment, ENSEngine
from frameworks.eu_ai_act_engine import EUAIActAssessment, EUAIActEngine
from frameworks.nis2_engine import NIS2Assessment, NIS2Engine
from ground_truth.ground_truth_evaluator import (
    GroundTruthEvaluationResult,
    GroundTruthEvaluator,
)
from ground_truth.pdf_ingestion import IngestedRegulatoryDocument
from ground_truth.rag_cag_mag_engine import RegulatoryMemoryTriad
from provenance.immutable_ledger import RegulatoryLedger
from provenance.merkle_bunker import MerkleAuditBunker, MerkleSeal

from .hitl_shield import RegulatoryBreachShield
from .telemetry import trace_compliance


class MeshEvaluationSummary(BaseModel):
    """Holistic multi-framework compliance verdict across the Live Mesh."""
    system_name: str
    global_score: float
    framework_scores: dict[str, float]
    dora: DORAAssessment
    nis2: NIS2Assessment
    ens: ENSAssessment
    eu_ai_act: EUAIActAssessment
    sbom: SBOMValidationResult
    seal: MerkleSeal | None = None
    all_passed: bool
    ground_truth_result: GroundTruthEvaluationResult | None = None
    assessed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LiveMeshOrchestrator:
    """Core engine orchestrating continuous compliance verification."""

    def __init__(self):
        self.dora_engine = DORAEngine()
        self.nis2_engine = NIS2Engine()
        self.ens_engine = ENSEngine()
        self.eu_ai_engine = EUAIActEngine()
        self.sbom_engine = CRASBOMEngine()
        self.ledger = RegulatoryLedger()
        self.bunker = MerkleAuditBunker()
        self.shield = RegulatoryBreachShield()
        self.ground_truth_triad: RegulatoryMemoryTriad | None = None

    def set_ground_truth_document(self, doc: IngestedRegulatoryDocument) -> RegulatoryMemoryTriad:
        """Sets the active ingested PDF as the authoritative Ground Truth memory."""
        self.ground_truth_triad = RegulatoryMemoryTriad(doc)
        return self.ground_truth_triad

    def evaluate_ground_truth(self, system_metadata: dict[str, Any]) -> GroundTruthEvaluationResult | None:
        """Audits system metadata against the active Ground Truth PDF."""
        if not self.ground_truth_triad:
            return None
        evaluator = GroundTruthEvaluator(self.ground_truth_triad)
        return evaluator.evaluate_system(system_metadata)

    @trace_compliance("LiveMesh.evaluate_event")
    def evaluate_event(
        self,
        event_name: str,
        system_metadata: dict[str, Any],
        packages: list[dict[str, str]] | None = None,
    ) -> MeshEvaluationSummary:
        """Executes full multi-framework continuous evaluation on an ingress event."""
        system_name = system_metadata.get("system_name", "Enterprise-Digital-Asset")

        # 1. Run all framework engines
        dora_res = self.dora_engine.evaluate(system_metadata)
        nis2_res = self.nis2_engine.evaluate(system_metadata)
        ens_res = self.ens_engine.evaluate(system_metadata)
        eu_ai_res = self.eu_ai_engine.evaluate(system_metadata)

        # 2. Run CRA SBOM engine
        default_pkgs = packages or [
            {"name": "fastapi", "version": "0.115.0", "license": "MIT", "vulnerabilities": 0},
            {"name": "pydantic", "version": "2.9.2", "license": "MIT", "vulnerabilities": 0},
            {"name": "uvicorn", "version": "0.31.0", "license": "BSD-3-Clause", "vulnerabilities": 0},
            {"name": "cryptography", "version": "43.0.1", "license": "Apache-2.0", "vulnerabilities": 0},
        ]
        sbom_res = self.sbom_engine.generate_and_audit(default_pkgs)

        # 3. Calculate scores
        scores = {
            "DORA": dora_res.overall_score,
            "NIS2": nis2_res.overall_score,
            "ENS (RD 311/2022)": ens_res.overall_score,
            "EU AI Act": eu_ai_res.overall_score,
            "CRA (CycloneDX)": 1.0 if sbom_res.cra_compliant else 0.5,
        }
        global_score = round(sum(scores.values()) / len(scores), 2)
        all_passed = (
            dora_res.compliant
            and nis2_res.compliant
            and ens_res.compliant
            and eu_ai_res.compliant
            and sbom_res.cra_compliant
        )

        # 4. Harvest evidences into Merkle Bunker
        self.bunker.add_evidence("DORA", "DORA_EVAL", dora_res.model_dump())
        self.bunker.add_evidence("NIS2", "NIS2_EVAL", nis2_res.model_dump())
        self.bunker.add_evidence("ENS", "ENS_EVAL", ens_res.model_dump())
        self.bunker.add_evidence("EU_AI_ACT", "EU_AI_EVAL", eu_ai_res.model_dump())
        self.bunker.add_evidence("CRA_SBOM", sbom_res.serial_number, sbom_res.model_dump())

        # Seal Merkle Tree
        seal = self.bunker.seal(system_name)

        # 5. Append event to Immutable Blockchain Ledger
        self.ledger.append_event(f"MESH_EVALUATION_{event_name.upper()}", {
            "system_name": system_name,
            "global_score": global_score,
            "merkle_root": seal.merkle_root_hash,
            "seal_id": seal.seal_id,
            "all_passed": all_passed,
        })

        # 6. Check for Critical Breaches -> Intercept with HITL Shield
        if not all_passed:
            failed_frameworks = [k for k, v in scores.items() if v < 0.85]
            self.shield.intercept_breach(
                framework=" / ".join(failed_frameworks),
                control_id="LIVE-MESH-GATE",
                description=f"Incumplimiento de umbral de resiliencia en {', '.join(failed_frameworks)}.",
                severity="HIGH",
                violations=[f"Puntuación insuficiente en {fw}: {scores[fw]*100}%" for fw in failed_frameworks],
            )

        # 2.5 Run Ground Truth if active
        gt_res = None
        if self.ground_truth_triad:
            gt_evaluator = GroundTruthEvaluator(self.ground_truth_triad)
            gt_res = gt_evaluator.evaluate_system(system_metadata)
            self.bunker.add_evidence("GROUND_TRUTH_PDF", gt_res.sha256_fingerprint, gt_res.model_dump())

        return MeshEvaluationSummary(
            system_name=system_name,
            global_score=global_score,
            framework_scores=scores,
            dora=dora_res,
            nis2=nis2_res,
            ens=ens_res,
            eu_ai_act=eu_ai_res,
            sbom=sbom_res,
            seal=seal,
            all_passed=all_passed and (gt_res.is_compliant if gt_res else True),
            ground_truth_result=gt_res,
        )
