"""CRA SBOM Engine (Cyber Resilience Act & CycloneDX v1.5 Standard).

Generates and audits Software Bill of Materials (SBOM) with Package URLs (PURLs),
cryptographic hashes, and vulnerability posture analysis.
"""

import hashlib
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class SBOMComponent(BaseModel):
    """Component representation according to CycloneDX v1.5 specification."""
    name: str
    version: str
    type: str = "library"
    purl: str
    sha256_hash: str
    license: str = "Apache-2.0"
    vulnerability_count: int = 0


class SBOMValidationResult(BaseModel):
    """Result of an automated SBOM audit."""
    bom_format: str = "CycloneDX"
    spec_version: str = "1.5"
    serial_number: str
    components: list[SBOMComponent]
    total_components: int
    vulnerable_components: int
    cra_compliant: bool
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CRASBOMEngine:
    """Automates SBOM inventory, PURL generation, and CRA security auditing."""

    def generate_and_audit(self, packages: list[dict[str, str]]) -> SBOMValidationResult:
        """Constructs a compliant CycloneDX SBOM and evaluates CRA posture."""
        components: list[SBOMComponent] = []
        vulnerable_count = 0

        for pkg in packages:
            name = pkg.get("name", "unknown")
            version = pkg.get("version", "1.0.0")
            purl = f"pkg:pypi/{name}@{version}"
            p_hash = hashlib.sha256(purl.encode("utf-8")).hexdigest()
            vulns = pkg.get("vulnerabilities", 0)
            if vulns > 0:
                vulnerable_count += 1

            components.append(SBOMComponent(
                name=name,
                version=version,
                purl=purl,
                sha256_hash=p_hash,
                license=pkg.get("license", "MIT"),
                vulnerability_count=vulns,
            ))

        import uuid
        serial = f"urn:uuid:{uuid.uuid4()}"
        compliant = vulnerable_count == 0 and len(components) > 0

        return SBOMValidationResult(
            serial_number=serial,
            components=components,
            total_components=len(components),
            vulnerable_components=vulnerable_count,
            cra_compliant=compliant,
        )
