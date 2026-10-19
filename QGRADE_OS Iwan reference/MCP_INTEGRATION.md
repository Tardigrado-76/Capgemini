# 🔌 MCP_INTEGRATION.md — QGRADE_OS The Maestro Cockpit
## Integración de Servidores Model Context Protocol Nativos (Zero Docker)

> **Estándar:** Model Context Protocol (Anthropic/Open-Source)  
> **Directiva Mandatoria:** 100% Nativo sin Docker. Transporte mediante `stdio` local (`npx`, `uvx`) o URLs remotas `SSE`.

---

## 1. Servidores MCP Asignados a QGRADE_OS

QGRADE_OS consume los siguientes MCPs para monitorizar, auditar y comunicar el estado del ecosistema:

```mermaid
graph LR
    Cockpit["👑 QGRADE_OS Cockpit"] --> SlackMCP["slack-mcp-server<br/><i>(Notificaciones & Approvals)</i>"]
    Cockpit --> GithubMCP["github-mcp-server<br/><i>(Control de Versiones y PRs)</i>"]
    Cockpit --> N8nMCP["n8n-mcp<br/><i>(Workflows & Webhooks)</i>"]
    Cockpit --> CloudflareMCP["cloudflare<br/><i>(WAF & Edge Gateway)</i>"]
    Cockpit --> PostgresMCP["postgres-mcp-server<br/><i>(Auditoría de Datos)</i>"]
```

---

## 2. Configuración Nativa para `mcp_config.json`

Añada o verifique estas entradas en `~/.gemini/antigravity-ide/mcp_config.json` o en la configuración global:

```json
{
  "mcpServers": {
    "slack-mcp-server": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-YOUR_SLACK_BOT_TOKEN",
        "SLACK_TEAM_ID": "T_YOUR_TEAM_ID"
      }
    },
    "github-mcp-server": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_GITHUB_TOKEN"
      }
    },
    "n8n-mcp": {
      "command": "npx",
      "args": ["-y", "n8n-mcp"],
      "env": {
        "N8N_API_URL": "http://localhost:5678",
        "N8N_API_KEY": "YOUR_N8N_API_KEY"
      }
    },
    "cloudflare": {
      "url": "https://mcp.cloudflare.com/mcp"
    }
  }
}
```

---

## 3. Catálogo de Herramientas Expuestas

| Servidor MCP | Herramienta | Firma / Payload | Propósito en el Cockpit |
| :--- | :--- | :--- | :--- |
| `slack-mcp-server` | `post_message` | `channel_id: str, text: str` | Emisión de alertas críticas de caída de servicio a los ingenieros de guardia. |
| `github-mcp-server` | `create_issue` | `repo: str, title: str, body: str` | Apertura de tickets automáticos ante violaciones de cumplimiento persistentes. |
| `n8n-mcp` | `search_templates` | `query: str, complexity: str` | Descubrimiento de recetas de automatización para orquestar flujos de remediación. |
| `cloudflare` | `dns_list_records` | `zone_id: str` | Verificación de resolución de nombres y salud de certificados TLS en endpoints. |
