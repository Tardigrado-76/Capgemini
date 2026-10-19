# 🛡️ WHITE CODING HARNESS (Proof Machine MVP)

> **Implementación de Referencia del Paradigma *White Coding* (Iwan Rochus van der Kleijn - Lead Architect & Director en Capgemini).**

---

## 🎯 ¿Qué es White Coding?

El término **White Coding** fue acuñado por Iwan van der Kleijn como el antídoto arquitectónico al *vibe coding* (generación descontrolada de código mediante prompts sin inspección, diseño previo ni límites estrictos).

En lugar de delegar a ciegas en LLMs o agentes no acotados:
1. **Whiteboard First:** Humanos y arquitectos diseñan formalmente en la pizarra: diagramas de secuencia/arquitectura (Mermaid), esquemas de datos (Pydantic/JSON Schema), invariantes y límites de contorno (imports prohibidos, presupuestos de archivos).
2. **Contract Lock:** La pizarra se traduce en contratos de paso inmutables (`StepContract`) con sellado criptográfico SHA-256.
3. **Bounded Generation:** Los agentes programadores operan confinados estrictamente dentro de la caja de arena y los límites de su contrato.
4. **Adversarial Evaluation:** Un evaluador independiente compila el código, ejecuta pruebas unitarias reales con `pytest` en un sandbox aislado y valida la conformidad AST/estática.
5. **Human-in-the-Loop (HITL) Gate:** Cualquier intento de violación de límites o desviación arquitectónica bloquea el despliegue y genera un ticket de aprobación humana.
```mermaid
graph TD
    subgraph Design ["1. Whiteboard First"]
        ARCH["WhiteboardArchitect<br/><i>Diseño Formal & Límites</i>"]
        SPEC["Especificación Declarativa<br/><i>Pydantic Invariants</i>"]
    end

    subgraph Lock ["2. Contract Lock"]
        CONTRACT["StepContract Lock<br/><i>SHA-256 Digest & AST Rules</i>"]
    end

    subgraph Gen ["3. Bounded Generation"]
        AGENT["Bounded Code Generator<br/><i>Confinado sin Imports Prohibidos</i>"]
    end

    subgraph Eval ["4. Adversarial Evaluation"]
        TEST["Sandbox Pytest Runner<br/><i>AdversarialEvaluator</i>"]
        HITL["HITL Approval Gate<br/><i>Art. 14 EU AI Act</i>"]
    end

    subgraph Bunker ["5. Cripto Búnker SLSA L3+"]
        LEDGER["Blockchain SHA-256"]
        MERKLE["Merkle Binary Tree"]
    end

    ARCH --> SPEC
    SPEC --> CONTRACT
    CONTRACT --> AGENT
    AGENT --> TEST
    TEST -->|Fallo o Límite Excedido| HITL
    TEST -->|Validación total superada| Bunker
    HITL -->|Aprobación Arquitecto| Bunker
```

## 📚 Documentación Técnica & Gobernanza
- 📖 [**Manual de Uso y Operación Detallado**](./MANUAL_DE_USO.md)
- 🤖 [**Especificación y Gobernanza de Agentes (AGENTS.md)**](./AGENTS.md)
- 🛠️ [**Catálogo de Skills Asignadas (SKILLS_REGISTRY.md)**](./SKILLS_REGISTRY.md)
- 🔌 [**Integración de Servidores MCP Nativos (MCP_INTEGRATION.md)**](./MCP_INTEGRATION.md)

---

## 🚀 Inicio Rápido (Doble Clic)

Simplemente ejecute el archivo:
```bat
INICIAR_WHITE_CODING_HARNESS.bat
```
El servidor ejecutivo Streamlit se iniciará automáticamente en:
**http://localhost:8506**

---

## 🧪 Ejecución de Pruebas Automatizadas

Para validar todos los subsistemas (especificación, contratos, límites, evaluador y búnker criptográfico):
```powershell
python -m pytest tests -v
```

---

## 🏛️ Estructura del Proyecto

```
WHITE CODING HARNESS/
├── INICIAR_WHITE_CODING_HARNESS.bat   # Lanzador ejecutable (Puerto 8506)
├── README.md                          # Este documento
├── app_streamlit.py                   # Consola Ejecutiva Streamlit
├── make_shortcut.py                   # Generador de acceso directo en escritorio
├── requirements.txt                   # Dependencias Python
│
├── core/                              # Núcleo de Orquestación y Contratos
│   ├── whiteboard_architect.py        # Generador de especificaciones y Mermaid
│   ├── contract_locker.py             # Bloqueo de StepContract y análisis AST
│   ├── bounded_generator.py           # Generador de código confinado
│   ├── adversarial_evaluator.py       # Evaluador adversarial y ejecutor de pruebas
│   ├── hitl_gate.py                   # Centro de aprobaciones Human-in-the-Loop
│   └── telemetry.py                   # ContextThreadPoolExecutor y OpenTelemetry
│
├── provenance/                        # Trazabilidad Criptográfica
│   ├── sha256_ledger.py               # Cadena de bloques inmutable
│   └── merkle_sealer.py               # Árbol binario de Merkle (SLSA L3+)
│
├── agent_workspace/sandbox/           # Directorio aislado de ejecución y pruebas
└── tests/                             # Suite de pruebas unitarias pytest (9 pruebas)
```
