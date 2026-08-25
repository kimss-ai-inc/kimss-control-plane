# AI Integration — Kimss Control Plane (Agent-to-Agent)

Instructions for coding agents, A2A clients, and automation that integrate with Kimss without rewriting application data planes.

## Core rules

1. **Never use `KimssClient` for chat/completions/messages.** Route inference through the native OpenAI or Anthropic SDK with a `base_url` change.
2. **Always send `X-Kimss-Agent-Id`** (and optionally `X-Kimss-Agent-Name`) on every inference request.
3. **OpenAI listener:** `base_url="https://api.kimss.ai/v1"` — SDK calls `/v1/chat/completions`.
4. **Anthropic listener:** `base_url="https://api.kimss.ai"` — SDK appends `/v1/messages`.
5. **Auth:** `Authorization: Bearer kimss_...`, `X-Kimss-Key: kimss_...`, or `x-api-key: kimss_...`.
6. **Control-plane API:** use the OpenAPI spec in [`openapi/control-plane.yaml`](openapi/control-plane.yaml) for registry, MCP RBAC, audit, metering, and kill switch — not chat endpoints.
7. **Hermis** is the Kimss orchestration framework (not LangGraph). The gateway + Hermis apply identity, kill switch, spend policy, and audit on every hop.

## Inference quick path

```python
from openai import OpenAI

client = OpenAI(
    api_key="kimss_...",
    base_url="https://api.kimss.ai/v1",
    default_headers={"X-Kimss-Agent-Id": "my-agent"},
)
```

Anthropic: see [docs/anthropic-onboarding.md](docs/anthropic-onboarding.md).

## Control-plane quick path

| Task | Endpoint | Doc |
|------|----------|-----|
| Check monthly cap | `GET /api/v1/governed-requests/meter` | OpenAPI |
| Register MCP server | `POST /api/v1/mcp-servers` | [`examples/`](examples/) |
| Grant MCP tool access | `POST /api/v1/mcp-servers/{name}/grants` | [`examples/mcp-tool-grant-*.json`](examples/) |
| Write audit event | `POST /audit_log/` | OpenAPI |
| Kill switch | `POST /agent_set_status/` | [`examples/agent-kill-switch-disable.json`](examples/) |

## Runnable tutorial

For copy-paste scripts and a local gateway simulator, use [kimss-python-quickstart](https://github.com/kimss-ai-inc/kimss-python-quickstart).

## Related

- [docs/anthropic-onboarding.md](docs/anthropic-onboarding.md)
- [kimss-python-sdk](https://github.com/kimss-ai-inc/kimss-python-sdk) — control-plane Python client
- [kimss.ai/trust](https://kimss.ai/trust) — security and compliance
