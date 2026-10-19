# 📦 SHARED QUANTIGRADE FOUNDATION
### *Núcleo Compartido de Identidad Visual, Tokens de Diseño y Sellado Pericial ReportLab*

---

## 🏛️ Visión y Propósito

`shared_quantigrade` es la librería transversal que alimenta a los 6 microservicios del ecosistema Capgemini Quantigrade. Proporciona consistencia visual de alta fidelidad (Glassmorphism, Cyber Blue `#00D2FF`, Navy `#0A1128`), carga unificada del logotipo corporativo y funciones de paginación y foliado judicial para los pasaportes emitidos en PDF.

```mermaid
graph TD
    Core["shared_quantigrade"] --> Theme["branding.py<br/><i>apply_quantigrade_theme()</i>"]
    Core --> PDF["pdf_branding.py<br/><i>add_quantigrade_header_footer()</i>"]
    Core --> Asset["assets/Quantigrade.jpg<br/><i>Logotipo Oficial 300 DPI</i>"]

    Theme --> WebCockpits["Paneles Ejecutivos Streamlit (:8500 - :8510)"]
    PDF --> Passports["Pasaportes Periciales & Dictámenes Oficiales"]
```

---

## 📚 Documentación Técnica & Gobernanza
- 📖 [**Manual de Uso y Operación Detallado**](./MANUAL_DE_USO.md)
- 🤖 [**Especificación y Gobernanza de Agentes (AGENTS.md)**](./AGENTS.md)
- 🛠️ [**Catálogo de Skills Asignadas (SKILLS_REGISTRY.md)**](./SKILLS_REGISTRY.md)
- 🔌 [**Integración de Servidores MCP Nativos (MCP_INTEGRATION.md)**](./MCP_INTEGRATION.md)

---

## 🧪 Pruebas Unitarias

```powershell
python -m pytest tests -v
```
Verifica la integridad de colores, el asset gráfico y la ausencia de colisiones de puertos en toda la suite.
