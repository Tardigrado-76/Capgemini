# AGENTS.md — COMPLIANCE-AS-CODE LIVE MESH
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
 AIACT_J["EU AI Act Officer<br/><i>Arts. 9, 12, 14, 27, 50</i>"]
 RGPD_J["RGPD / DPO Judge<br/><i>TOMs, EIPD, Brechas 72h</i>"]
 CRA_J["CRA Supply-Chain Auditor<br/><i>CycloneDX v1.6 & Dual-Sign</i>"]
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
- **Competencias:** Auditar políticas de ciberhigiene (Art. 21) y verificar mecanismos de alerta temprana al CSIRT (<24h para incidentes significativos ante CCN-CERT/INCIBE).

### C. ENS Lead Auditor
- **Marco:** Real Decreto 311/2022 (Esquema Nacional de Seguridad) y Guías CCN-STIC (807, 812, 883).
- **Competencias:** Control estricto de accesos privilegiados [op.acc.1], registro inmutable de actividad [op.exp.8], cifrado en tránsito/reposo [mp.com.1] y separación rigurosa de funciones en categoría ALTA.

### D. EU AI Act Officer
- **Marco:** Reglamento (UE) 2024/1689 de Inteligencia Artificial.
- **Competencias:** Supervisión humana efectiva y kill-switch (Art. 14), registro inmutable de trazabilidad (Art. 12), ciberseguridad (Art. 15), evaluación de impacto en derechos fundamentales (FRIA Art. 27) y marcas de agua de contenido sintético (Art. 50).

### E. RGPD & LOPDGDD Data Protection Officer (DPO Judge)
- **Marco:** Reglamento (UE) 2016/679 (RGPD) y Ley Orgánica 3/2018 (LOPDGDD).
- **Competencias:** Verificación de medidas técnicas y organizativas TOMs (Art. 32), Evaluación de Impacto EIPD/DPIA para IA (Art. 35), protocolo de notificación de brechas en <72h ante la AEPD (Art. 33), destrucción criptográfica / crypto-shredding (Art. 17) y registro de actividades de tratamiento RAT (Art. 30).

### F. CRA Supply-Chain Auditor
- **Marco:** Reglamento (UE) 2024/2847 (Cyber Resilience Act).
- **Competencias:** Inventario automatizado CycloneDX v1.6 SBOM (Art. 11), firma dual (ECDSA + FIPS 204 ML-DSA), eliminación de credenciales por defecto (Art. 10), actualizaciones firmadas (Art. 10.4) y divulgación VEX (Art. 13).

---

## 3. Directrices de Razonamiento Agnóstico al Modelo
1. Cada evaluación debe mapear los hallazgos a los identificadores exactos de los controles regulatorios (ej. `DORA-ICT-01`, `NIS2-CYBER-03`, `ENS-ACC-05`).
2. Todo incumplimiento crítico bloquea el despliegue de forma determinista salvo override firmado por el CISO humano.
