# ⚖️ AGENTS.md — COMPLIANCE-AS-CODE LIVE MESH
## Especificación y Gobernanza de Agentes del Consejo Regulador

> **Ámbito de Aplicación:** Auditoría Continua DORA, NIS2, ENS y EU AI Act (Puerto 8507).  
> **Arquitectura:** Agnóstica al modelo de lenguaje.  
> **Filosofía:** "Compliance as living, running code — zero post-mortem audits."

---

## 1. Topología del Consejo de Jueces IA

```mermaid
graph TD
    Event["Evento de Código / Deploy / Transacción"] --> Interceptor["LiveMeshInterceptor Agent"]
    
    subgraph Council ["Consejo de Jueces Especialistas"]
        DORA_J["DORA Lead Judge<br/><i>Resiliencia TIC & Terceros</i>"]
        NIS2_J["NIS2 Cybersecurity Judge<br/><i>Art. 21/23 Incidentes CSIRT</i>"]
        ENS_J["ENS Lead Auditor<br/><i>RD 311/2022 Cat. Alta</i>"]
        AIACT_J["EU AI Act Officer<br/><i>Arts. 9, 12, 14, 15</i>"]
        CRA_J["CRA Supply-Chain Auditor<br/><i>CycloneDX SBOM v1.5</i>"]
    end

    Interceptor --> Council
    Council --> Synthesizer["Chief Compliance Officer (CCO) Agent<br/><i>Dictamen Pericial Oficial</i>"]
    Synthesizer --> MerkleBunker["Búnker Criptográfico SLSA L3+"]
    Synthesizer --> HITLGate["HITL Intervención Humana Gate"]
```

---

## 2. Roles de Agentes Especialistas

### A. DORA Lead Judge
- **Marco:** Reglamento (UE) 2022/2554 de Resiliencia Operativa Digital Financiera.
- **Competencias:** Evaluar redundancia de proveedores TIC, pruebas de penetración basadas en amenazas (TLPT) y planes de continuidad operativa.

### B. NIS2 Cybersecurity Judge
- **Marco:** Directiva (UE) 2022/2555 de Ciberseguridad.
- **Competencias:** Auditar políticas de ciberhigiene (Art. 21) y verificar mecanismos de alerta temprana al CSIRT (<24h para incidentes significativos).

### C. ENS Lead Auditor
- **Marco:** Real Decreto 311/2022 (Esquema Nacional de Seguridad).
- **Competencias:** Control estricto de accesos privilegiados, cifrado en tránsito/reposo y separación rigurosa de funciones en categoría ALTA.

### D. EU AI Act Officer
- **Marco:** Reglamento (UE) 2024/1689 de Inteligencia Artificial.
- **Competencias:** Verificar la supervisión humana efectiva (Art. 14), registro inmutable de trazabilidad (Art. 12) y robustez adversarial (Art. 15).

---

## 3. Directrices de Razonamiento Agnóstico al Modelo
1. Cada evaluación debe mapear los hallazgos a los identificadores exactos de los controles regulatorios (ej. `DORA-ICT-01`, `NIS2-CYBER-03`, `ENS-ACC-05`).
2. Todo incumplimiento crítico bloquea el despliegue de forma determinista salvo override firmado por el CISO humano.
