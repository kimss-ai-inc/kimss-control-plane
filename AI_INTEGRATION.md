# AI Integration — Kimss Control Plane (Agent-to-Agent)

**Canonical public A2A contract** for Cursor, Cascade, Claude Code, Windsurf, Devin, and other coding assistants.

Kimss is a **Model-Agnostic Enterprise AI Gateway and Governance Control Plane** with a **dual-listener** inbound proxy:

- OpenAI syntax → `POST https://api.kimss.ai/v1/chat/completions`
- Anthropic syntax → `POST https://api.kimss.ai/v1/messages`

This file is the **primary** integration spec Cascade / Cursor should fetch. Runtime SSOT remains `kimssApi`; this repo is the public contract hub — **do not clone control-plane source into the customer app**.

## Prerequisites (Kimss app — before repo changes)

Complete these in the Kimss UI **before** rewiring application code:

1. **Provider Vault** (`/app/vault`): register each `custom:<model_id>` you will call. One vault row per model alias; you may reuse the same provider API key when registering multiple models.
2. **Gateway API key** (`/app/keys`): mint a `kimss_...` workspace key. Never put the provider key in application source code.
3. **Route traffic**: set `OPENAI_BASE_URL=https://api.kimss.ai/v1` (or Anthropic `base_url=https://api.kimss.ai`) and use the Gateway API key as `OPENAI_API_KEY` / `api_key`.

If a model is not vaulted, Kimss returns an error pointing to Provider Vault. **Agents Discovery** (`/app/agents`) populates automatically after the first governed request that includes `X-Kimss-Agent-Id` — you do not need to create agents in the UI first.

## Rules (do not violate)

1. **Never** use a custom `KimssClient` for chat/completions/messages or any LLM inference.
2. **Identify** whether the user's codebase uses the `openai` or `anthropic` SDK natively. **Keep their native SDK** — zero data-plane refactoring.
3. **For OpenAI:** set `base_url` to `https://api.kimss.ai/v1`.
4. **For Anthropic:** set `base_url` to `https://api.kimss.ai` (the SDK appends `/v1/messages`).
5. **Always** inject `X-Kimss-Agent-Id` (and preferably `X-Kimss-Agent-Name`) for JIT attribution, audit, and kill-switch.
6. **Call-site visibility (recommended):** when `kimss` is installed, use `kimss.gateway_headers(agent_id=..., agent_name=...)` as `extra_headers`. A plain `extra_headers={"X-Kimss-Agent-Id": "..."}` dict is enough.
7. Hermis / HTTP interceptors: forward Agent-Id headers; never strip them.
8. **Control-plane API** (registry, MCP RBAC, audit, metering, kill switch): use [`openapi/control-plane.yaml`](openapi/control-plane.yaml) — not chat endpoints.
9. **Hermis** is the Kimss orchestration framework (not LangGraph). The gateway + Hermis apply identity, kill switch, spend policy, and audit on every hop.

## OpenAI

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.kimss.ai/v1",  # required
    api_key="kimss_workspace_key",  # required Gateway key, not the provider key
    default_headers={"X-Kimss-Agent-Id": "my-service"},
)
response = client.chat.completions.create(
    model="custom:your-model-id",  # required — vaulted alias
    messages=[{"role": "user", "content": "Execute audit."}],
)
```

## Anthropic

```python
from anthropic import Anthropic

client = Anthropic(
    base_url="https://api.kimss.ai",
    api_key="kimss_workspace_key",
    default_headers={"X-Kimss-Agent-Id": "my-service"},
)
response = client.messages.create(
    model="custom:your-model-id",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Execute audit."}],
)
```

Full Anthropic env-var path and troubleshooting: [docs/anthropic-onboarding.md](docs/anthropic-onboarding.md).

Auth also accepts `X-Kimss-Key` and Anthropic-style `x-api-key` with a `kimss_...` workspace key.

## What `KimssClient` is for

Control-plane / DevOps only (`agents.register`, `usage.report`). Inference methods are deprecated. Prefer this file + native SDKs for chat.

## Kill switch

HTTP **403** with `agent_disabled` (OpenAI `error.code` or Anthropic error body).

## Control-plane quick path

| Task | Endpoint | Doc |
|------|----------|-----|
| Check monthly cap | `GET /api/v1/governed-requests/meter` | OpenAPI |
| Register MCP server | `POST /api/v1/mcp-servers` | [`examples/`](examples/) |
| Grant MCP tool access | `POST /api/v1/mcp-servers/{name}/grants` | [`examples/mcp-tool-grant-*.json`](examples/) |
| Write audit event | `POST /audit_log/` | OpenAPI |
| Kill switch | `POST /agent_set_status/` | [`examples/agent-kill-switch-disable.json`](examples/) |

## Runnable tutorial

For copy-paste scripts and a local gateway simulator, use [kimss-python-quickstart](https://github.com/kimss-ai/kimss-python-quickstart).

## Related

- Product route guide: https://kimss.ai/docs/route_traffic
- [docs/anthropic-onboarding.md](docs/anthropic-onboarding.md)
- [kimss-python-sdk](https://github.com/kimss-ai/kimss-python-sdk) — optional control-plane Python client (`pip install kimss`)
- [kimss.ai/trust](https://kimss.ai/trust) — security and compliance
