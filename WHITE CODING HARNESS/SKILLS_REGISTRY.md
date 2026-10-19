# ⚡ SKILLS_REGISTRY.md — WHITE CODING HARNESS
## Catálogo y Runbooks de Habilidades para el Confinamiento de Código

> **Referencia de Skills:** Documentadas en `SKILLS INSTALADAS EN ANTIGRAVY.docx`  
> **Directiva:** Rigor formal Red-Green TDD y cero tolerancia a errores estáticos.

---

## 1. Matriz de Skills Aplicables a White Coding

| Skill | Categoría | Utilidad Concreta en White Coding | Trigger de Activación |
| :--- | :--- | :--- | :--- |
| **`test-driven-development`** | Metodología | Creación de tests unitarios antes de permitir la generación de código (`Red ➔ Green`). | En cada nuevo `StepContract`. |
| **`systematic-debugging`** | Diagnóstico | Protocolo de 4 fases para investigar la causa raíz de fallos en el evaluador adversarial. | Cuando un test de `pytest` falla durante la evaluación. |
| **`code-doctor`** | Calidad de Código | Auditoría automática estricta de Python (`ruff`, `mypy`, `bandit`). | Tras cada generación de código por el `BoundedGenerator`. |
| **`ponytail`** | Ingeniería Senior | Minimización radical de líneas de código generadas, eliminando código defensivo innecesario. | En la fase de escritura y refactorización. |
| **`verification-before-completion`** | Aseguramiento | Obligación de ejecutar y verificar la salida del comando de prueba antes de reportar éxito. | Antes de cerrar cualquier tarea o emitir veredicto. |
| **`openspec-*`** | Especificación | Workflow declarativo spec ➔ delta ➔ implementación para gobernar cambios de arquitectura. | Al modificar o añadir un nuevo componente central. |

---

## 2. Protocolo de Ejecución de TDD Estricto

1. **Paso 1 (Red):** El `WhiteboardArchitect` genera el archivo `tests/test_<feature>.py` definiendo los casos de prueba esperados. Ejecución obligatoria confirmando fallo inicial:
   ```powershell
   python -m pytest tests/test_<feature>.py -v
   ```
2. **Paso 2 (Green):** El `BoundedGenerator` escribe la implementación mínima en `core/<feature>.py` respetando el `StepContract`.
3. **Paso 3 (Audit):** El `AdversarialEvaluator` corre `code-doctor`:
   ```powershell
   python -m ruff check core/<feature>.py --fix
   python -m bandit -r core/<feature>.py -ll
   ```
4. **Paso 4 (Seal):** Con 100% de tests pasando y 0 lints, se sella el hash del diff en el blockchain SHA-256.
