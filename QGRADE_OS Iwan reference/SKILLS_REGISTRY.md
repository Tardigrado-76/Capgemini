# ⚡ SKILLS_REGISTRY.md — QGRADE_OS The Maestro Cockpit
## Catálogo y Runbooks de Habilidades Operativas para el Orquestador

> **Referencia de Skills:** Documentadas en `SKILLS INSTALADAS EN ANTIGRAVITY.docx`  
> **Modo de Activación:** Progresivo y bajo demanda (Lazy Loading).

---

## 1. Matriz de Skills Aplicables a QGRADE_OS

| Skill | Categoría | Utilidad Concreta en QGRADE_OS | Trigger de Activación |
| :--- | :--- | :--- | :--- |
| **`swarms`** | Multi-Agente | Orquestación de topologías concurrentes y jerárquicas entre los agentes del Cockpit. | Cuando se requiere coordinar múltiples subagentes en paralelo. |
| **`litellm`** | Orquestación LLM | Enrutamiento inteligente multi-modelo, balanceo de carga y fallback automático ante caídas de proveedores. | Cuando se invocan modelos de inferencia o evaluación externa. |
| **`cubesandbox`** | Sandboxing | Ejecución segura y aislada de comandos externos sin riesgo para el sistema anfitrión. | Cuando el agente ejecuta diagnósticos en microprocesos. |
| **`code-doctor`** | Calidad de Código | Auditoría estricta continua de Python (`ruff`, `mypy`, `bandit`) sobre el código del Cockpit. | Previo a cualquier refactorización o cambio en el orquestador. |
| **`ui-ux-pro-max`** | Diseño UI/UX | Optimización visual del panel de control Streamlit, paletas slate navy y micro-interacciones. | Al diseñar o modificar vistas ejecutivas y dashboards. |
| **`brand`** | Identidad de Marca | Cumplimiento del manual de estilo oficial de Quantigrade y posicionamiento corporativo. | Al generar informes, cabeceras o dossiers PDF. |
| **`systematic-debugging`** | Diagnóstico | Protocolo de 4 fases para investigar anomalías de red o puertos colisionados. | Cuando un microservicio reporta `PORT_ERROR` o `TIMEOUT`. |

---

## 2. Runbooks Operativos Paso a Paso

### Runbook 1: Balanceo y Fallback Multi-Modelo con `litellm`
1. **Detección:** Si el proveedor primario (ej. Claude 3.5 Sonnet o Gemini Pro) excede cuota o latencia > 4000ms.
2. **Fallback:** Derivar la consulta a un modelo secundario configurado en la cadena de fallback sin interrumpir la sesión del operador.
3. **Registro:** Loguear el coste y consumo de tokens en el ledger local para control presupuestario.

### Runbook 2: Auditoría Integral con `code-doctor`
1. Ejecutar auto-revisión de sintaxis y lints: `python -m ruff check . --fix`
2. Validar tipos estáticos: `mypy --ignore-missing-imports .`
3. Ejecutar escáner de seguridad AST: `bandit -r . -ll`
4. Confirmar que se mantiene el estándar de **0 errores y 0 vulnerabilidades**.
