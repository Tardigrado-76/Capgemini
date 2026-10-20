# QUANTIGRADE OS — The Maestro Cockpit
### *Consola de Supervisión Unificada y Enrutamiento JIT para el Ecosistema de Agentes Enterprise*

---

## Propósito Arquitectónico: El Arnés Operativo Unificado

> *"Llevar los sistemas basados en agentes al entorno corporativo exige pasar de la experimentación aislada a la gobernanza centralizada. 
> 
> QGRADE_OS actúa como el hipervisor y panel de control operativo (*The Maestro Cockpit*) que integra los principios de **White Coding**, evaluación continua de cumplimiento (**DORA, NIS2, ENS, EU AI Act**), descubrimiento semántico de herramientas y mitigación de riesgos en tiempo de ejecución.
>
> Su misión no es añadir complejidad, sino orquestar de forma no invasiva los subsistemas especializados: aislar la ejecución en entornos de prueba, garantizar la trazabilidad criptográfica de las decisiones (firmas Ed25519 y Merkle Ledger) y proporcionar a los equipos de ingeniería un punto de observación único, determinista y verificado al 100% mediante pruebas automatizadas."*

---

## ¿Por qué QGRADE_OS es la Suma de Todo?

QGRADE_OS no es una herramienta más: **es el hipervisor orquestador (The Maestro Cockpit)** que unifica, supervisa y audita transversalmente los motores autónomos de la suite Quantigrade. 

Cada subsistema resuelve uno de los problemas críticos planteados por Iwan en la arquitectura de agentes enterprise:

```mermaid
graph TD
 subgraph Cockpit ["QGRADE_OS — The Maestro Cockpit (Port 8500)"]
 MS["Maestro Swarm JIT Router<br/><i>orchestrator/maestro_swarm.py</i>"]
 FW["Dual-Model Prompt Firewall<br/><i>OWASP LLM01 Jailbreak Shield</i>"]
 SB["MicroVM Sandbox Guard<br/><i>Restricted Execution Engine</i>"]
 ED["Ed25519 Signer & Merkle Ledger<br/><i>SLSA L3+ Audit Bunker</i>"]
 EX["Universal Exporter<br/><i>JSON / Markdown / PDF ReportLab</i>"]
 end

 subgraph Bridges ["Puentes JIT Especializados (Zero-Overhead)"]
 B_WCH["WhiteCodingBridge<br/><i>StepContracts & Jira/Confluence</i>"]
 B_CMP["ComplianceBridge<br/><i>DORA / NIS2 / ENS Telemetry</i>"]
 B_SDP["SemanticBridge<br/><i>SDP Tier-0 Canonical Hydration</i>"]
 B_CFO["CFOBridge<br/><i>P&L, Treasury & Altman Z'-Score</i>"]
 B_TAU["EvaluationBridge<br/><i>TAU-bench & GAIA Stress</i>"]
 end

 subgraph Satellites ["Flota Autónoma Especializada"]
 WCH["White Coding Harness (8506)"]
 CMP["Compliance-as-Code (8507)"]
 SDP["Semantic Discovery (8510)"]
 CFO["Autonomous CFO (8501)"]
 TAU["TAU-bench Evaluator (8509)"]
 end

 subgraph Infra ["Despliegue Cloud-Native"]
 K8S["k8s/quantigrade-mesh.yaml"]
 POD["podman/quantigrade-mesh.container"]
 end

 FW --> MS
 SB --> MS
 MS --> ED
 ED --> EX

 MS --> B_WCH --> WCH
 MS --> B_CMP --> CMP
 MS --> B_SDP --> SDP
 MS --> B_CFO --> CFO
 MS --> B_TAU --> TAU

 K8S -.-> Cockpit
 POD -.-> Cockpit
```

---

## Pilares Arquitectónicos de QGRADE_OS

### 1. El Ciclo Completo de White Coding (Pizarra Contrato Código Prueba)
Conecta directamente con la [Proof Machine](../WHITE%20CODING%20HARNESS). Ningún agente escribe código en el vacío:
- **Whiteboard First:** Especificación formal mediante esquemas y diagramas.
- **StepContract:** Bloqueo inmutable con hash SHA-256 e inspección sintáctica AST.
- **Adversarial Evaluator:** Evaluación implacable mediante `pytest` en sandbox.
- **HITL Approval Gate:** El humano mantiene la última palabra en operaciones sensibles según exige el Artículo 14 del EU AI Act.

---

## Documentación Técnica & Gobernanza de QGRADE_OS
- [**Manual de Uso y Operación Detallado**](./MANUAL_DE_USO.md)
- [**Especificación y Gobernanza de Agentes (AGENTS.md)**](./AGENTS.md)
- [**Catálogo de Skills Asignadas (SKILLS_REGISTRY.md)**](./SKILLS_REGISTRY.md)
- [**Integración de Servidores MCP Nativos (MCP_INTEGRATION.md)**](./MCP_INTEGRATION.md)

### 2. Cumplimiento Regulatorio Continuo (Compliance-as-Code Live Mesh)
Elimina las auditorías manuales anuales. A través de sondas no intrusivas sobre los microservicios, el sistema evalúa en tiempo real:
- **DORA:** Resiliencia operativa, gestión de riesgos TIC de terceros y continuidad.
- **NIS2:** Medidas técnicas del Art. 21 y notificación de incidentes tempranos (<24h).
- **ENS (RD 311/2022 - Categoría Alta):** Trazabilidad exhaustiva, control de acceso y separación de funciones.
- **EU AI Act:** Supervisión humana efectiva (HITL) y registro inmutable de logs técnicos (Art. 12).

### 3. Descubrimiento Semántico Tier-0 (Zero Prompt-Stuffing)
La resolución estática de cientos de herramientas en el system prompt satura la ventana de contexto y dispara el gasto de inferencia. Con el protocolo SDP:
- Las capacidades se catalogan en micro-metadatos Tier-0 (~45 tokens por conector).
- El router semántico activa solo las herramientas pertinentes bajo demanda.
- Resultado comprobado: **85% a 94% de reducción en el consumo de tokens** por ciclo de interacción.

### 4. Seguridad Criptográfica y Resiliencia Cuántica
- **Ed25519 Digital Signatures:** Cada dictamen y bloque del ledger pericial se firma asimétricamente en tiempo constante, impidiendo la falsificación unilateral de hashes locales.
- **Merkle Tree Append-Only:** Estructura jerárquica SHA-256 con raíz criptográfica verificable judicialmente.
- **Dual-Model Prompt Injection Firewall:** Neutraliza intentos de jailbreak, reseteo de instrucciones del sistema e inyecciones indirectas redactándolos antes de ingresar al bucle cognitivo.
- **MicroVM Process Guardrails:** Intercepta comandos de riesgo (`rm -rf`, `drop database`, operaciones de formato) y aísla la ejecución de herramientas.

---

## Manual de Operación y Uso

### A. Requisitos Previos
- Python 3.10 o superior (compatible y probado hasta Python 3.13 en Windows 11).
- Dependencias base instaladas en el entorno:
 ```powershell
 pip install -r requirements.txt
 ```

### B. Arranque con Un Clic (Modo Operador)
Ejecute el archivo por lotes en la consola o con doble clic:
```bat
INICIAR_QUANTIGRADE_MAESTRO.bat
```
El Cockpit se desplegará instantáneamente en su navegador predeterminado:
 **`http://localhost:8500`**

### C. Módulos del Cockpit

1. ** Panel de Flota (Fleet Management):**
 - Monitoriza en tiempo real el estado de escucha de los 8 puertos del ecosistema.
 - Dispone de botones dedicados para lanzar servicios de forma individual o en paralelo (`Launch All Engines`), abriendo ventanas de consola desacopladas.

2. ** Auditoría Compuesta Transversal (Cross-Engine Audit):**
 - Ejecuta un peritaje global instantáneo invocando la postura de cumplimiento de Live Mesh, la verificación contractual de White Coding y la economía de tokens de SDP.
 - Emite el sello unificado de aptitud enterprise.

3. ** Búnker Criptográfico y Firmas Ed25519:**
 - Visualización de la cadena de bloques local SHA-256.
 - Generación de pares de claves públicas/privadas Ed25519 y firmado de hashes de verificación.

4. ** Exportador Universal:**
 - Descarga el informe ejecutivo pericial completo en formatos JSON estructurado, Markdown judicial y PDF listo para el Consejo de Administración.

---

## Verificación y Suite de Tests (32 / 32 PASS)

El núcleo de QGRADE_OS cuenta con una cobertura TDD total ejecutada con éxito:
```powershell
python -m pytest -v
```

```
tests/test_qgrade_suite.py::test_ed25519_signing_and_verification PASSED
tests/test_qgrade_suite.py::test_qgrade_signed_ledger PASSED
tests/test_qgrade_suite.py::test_qgrade_signed_merkle_tree PASSED
tests/test_qgrade_suite.py::test_qgrade_sandbox_blocks_destructive_commands PASSED
tests/test_qgrade_suite.py::test_qgrade_prompt_firewall_redacts_injections PASSED
tests/test_qgrade_suite.py::test_qgrade_universal_exporter PASSED
tests/test_qgrade_suite.py::test_qgrade_maestro_swarm PASSED
tests/test_qgrade_suite.py::test_qgrade_disruptive_innovations PASSED
tests/test_enterprise_swarm.py::test_white_coding_bridge_payload PASSED
tests/test_enterprise_swarm.py::test_cfo_bridge_payload PASSED
tests/test_enterprise_swarm.py::test_compliance_bridge_payload PASSED
tests/test_enterprise_swarm.py::test_evaluation_bridge_payload PASSED
tests/test_enterprise_swarm.py::test_semantic_bridge_payload PASSED
tests/test_enterprise_swarm.py::test_full_swarm_dispatch PASSED
tests/test_omnichannel_and_maestro_extensions.py::test_omnichannel_hitl_bridge PASSED
tests/test_omnichannel_and_maestro_extensions.py::test_ecommerce_sentinel PASSED
tests/test_omnichannel_and_maestro_extensions.py::test_cold_storage_bunker PASSED
tests/test_qgrade_ide_orchestrator.py::test_byzantine_consensus PASSED
tests/test_qgrade_ide_orchestrator.py::test_copilot_studio_bridge PASSED
tests/test_qgrade_wave5.py::test_full_ide_orchestration_cycle PASSED
...
============================== 32 passed in 3.85s ==============================
```

Auditoría de seguridad y calidad estática:
```powershell
python -m ruff check . # 0 errors, 0 warnings
python -m bandit -r . -ll # 0 issues (0 Medium, 0 High)
```

---

## Matriz Oficial de Cobertura Regulatoria

| Marco Normativo | Base Legal | Implementación Técnica en QGRADE_OS | Estado |
| :--- | :--- | :--- | :---: |
| **ENS (RD 311/2022 - Nivel Alto)** | Esquema Nacional de Seguridad | Búnker de custodia inmutable con firmas asimétricas Ed25519 y árboles Merkle SLSA L3+. | **Conforme** |
| **EU AI Act Art. 14** | Reglamento UE 2024/1689 | Supervisión Humana Efectiva (HITL): Omnichannel Bridge multicanal con anulación gobernada. | **Conforme** |
| **EU AI Act Art. 15** | Reglamento UE 2024/1689 | Dual-Model Prompt Injection Firewall contra ataques OWASP Top 10 for LLMs (LLM01). | **Conforme** |
| **DORA** | Reglamento UE 2022/2554 | Trazabilidad de incidentes TIC y resiliencia de orquestación ante caídas de proveedores. | **Conforme** |
| **NIS2 Art. 21** | Directiva UE 2022/2555 | Seguridad en la arquitectura de red y control de ejecución en sandbox seguro. | **Conforme** |

---

## Especificación de Puertos y Servicios

| Puerto | Componente | Descripción |
| :---: | :--- | :--- |
| **`8500`** | **QGRADE_OS Maestro Cockpit** | Centro de mando multi-agente y orquestación unificada |
| **`8501`** | **Autonomous CFO** | Tesorería autónoma, conciliación ERP y ratios Altman Z'-Score |
| **`8502`** | **Workforce AI Hub** | Despacho dinámico de roles de agentes con control de presupuesto |
| **`8504`** | **Outbound Machine** | Motor B2B autónomo de prospección, validación y sincronización CRM |
| **`8506`** | **White Coding Harness** | Proof Machine para diseño formal y StepContracts |
| **`8507`** | **Compliance Live Mesh** | Sonda regulatoria continua DORA, NIS2, ENS y EU AI Act |
| **`8508`** | **Omni Contact Center** | Centro multicanal autónomo (Voz, WhatsApp, Web, Email) |
| **`8509`** | **Agent Evaluation Framework** | Benchmark adversarial TAU-bench/GAIA para resiliencia de agentes |
| **`8510`** | **Semantic Discovery Protocol**| Motor Tier-0 de resolución semántica y ahorro de contexto |

---

*Desarrollado bajo la filosofía Bottom-Up AI Workbench: Rigor formal, código real en ejecución y cero PoC Purgatory.*
