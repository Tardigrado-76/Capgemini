# MCP_INTEGRATION.md — SHARED QUANTIGRADE
## Integración de Servidores Model Context Protocol (Zero-Docker Native)

> **Directiva Mandatoria:** Cero dependencias de contenedores Docker. Todos los servicios se ejecutan nativamente en el host.

---

## 1. Conexiones MCP para la Librería Base

La librería `shared_quantigrade` interactúa con los siguientes servidores nativos para el despliegue y distribución de activos:

| Servidor MCP | Runtime / Transporte | Propósito Operativo |
| :--- | :--- | :--- |
| **`github-mcp-server`** | `npx -y @modelcontextprotocol/server-github` (`stdio`) | Publicación de releases versionadas de la librería y sincronización de submódulos. |
| **`puppeteer-mcp`** | `npx -y @modelcontextprotocol/server-puppeteer` (`stdio`) | Pruebas de regresión visual automatizadas (capturas de pantalla y pixel-matching) de los temas aplicados. |

---

## 2. Configuración Nativa de Referencia (`mcp_config.json`)

```json
{
 "mcpServers": {
 "github": {
 "command": "npx",
 "args": ["-y", "@modelcontextprotocol/server-github"],
 "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}" }
 },
 "puppeteer": {
 "command": "npx",
 "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
 }
 }
}
```
