# Kimss Control Plane

[![License: MIT](https://img.shields.io/badge/License-MIT-indigo.svg)](LICENSE)
[![CI](https://github.com/kimss-ai/kimss-control-plane/actions/workflows/ci.yml/badge.svg)](https://github.com/kimss-ai/kimss-control-plane/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/kimss-ai/kimss-control-plane/badge)](https://scorecard.dev/viewer/?uri=github.com/kimss-ai/kimss-control-plane)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/14243/badge)](https://www.bestpractices.dev/en/projects/14243)

**Public hub for the Kimss Secure Enterprise Agent Control Plane** — a model-agnostic API gateway for enterprise AI agents, MCP RBAC, and agent-to-agent integration.

Kimss is not a chat platform. Customers bring their own agents, models, and infrastructure. Kimss provides registry, SSO identity mapping, MCP RBAC, governed-request metering, gateway-verified audit (Article 12 path), and an authoritative kill switch at the gateway.

**Live API:** `https://api.kimss.ai`

<p align="center">
  <img src="docs/hero-control-plane.svg" alt="Kimss control plane: agents and SDKs connect through identity, policy, audit, metering, and kill switch before reaching vaulted providers and MCP infrastructure." width="100%">
</p>

---

## Start here

| Goal | Where to go |
|------|-------------|
| Route OpenAI / Anthropic traffic in 5 minutes | [kimss-python-quickstart](https://github.com/kimss-ai/kimss-python-quickstart) |
| Anthropic onboarding (SDK + env vars + troubleshooting) | [docs/anthropic-onboarding.md](docs/anthropic-onboarding.md) |
| Python control-plane SDK (`pip install kimss`) | [kimss-python-sdk](https://github.com/kimss-ai/kimss-python-sdk) |
| Java control-plane SDK (Maven `com.kimss:kimss-java`) | [kimss-java-sdk](https://github.com/kimss-ai/kimss-java-sdk) |
| Agent-to-agent integration rules | [AI_INTEGRATION.md](AI_INTEGRATION.md) |
| Product docs & trust center | [kimss.ai](https://kimss.ai) · [Trust Center](https://kimss.ai/trust) |

---

## Product integration — one-line gateway change

### OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    api_key="kimss_...",
    base_url="https://api.kimss.ai/v1",
    default_headers={"X-Kimss-Agent-Id": "my-agent"},
)
```

### Anthropic SDK

```python
from anthropic import Anthropic

client = Anthropic(
    api_key="kimss_...",
    base_url="https://api.kimss.ai",
    default_headers={"X-Kimss-Agent-Id": "my-agent"},
)
```

The Anthropic SDK appends `/v1/messages`. Full setup, env-var path, and troubleshooting: **[docs/anthropic-onboarding.md](docs/anthropic-onboarding.md)**.

**Auth:** `Authorization: Bearer kimss_...`, `X-Kimss-Key`, or `x-api-key: kimss_...`.

---

## Agent-to-agent (A2A)

**Canonical Cascade / Cursor / Claude Code fetch URL:**

```text
https://raw.githubusercontent.com/kimss-ai/kimss-control-plane/main/AI_INTEGRATION.md
```

Product paste prompts (Vault → Connect your app → AI coding agent) and [`/docs/route_traffic`](https://kimss.ai/docs/route_traffic) point here — not at the SDK mirror.

Coding agents and automation should:

1. Keep native OpenAI or Anthropic SDKs — **never** use `KimssClient` for chat/completions.
2. Always send `X-Kimss-Agent-Id` on inference requests.
3. Use [`openapi/control-plane.yaml`](openapi/control-plane.yaml) for registry, MCP grants, audit, metering, and kill switch.

See **[AI_INTEGRATION.md](AI_INTEGRATION.md)** for the full contract.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `401` / invalid API key | Wrong or missing `kimss_...` key | Mint a new key under **Gateway → Generate Key** |
| `400` / missing agent | No `X-Kimss-Agent-Id` header | Set agent id and pass via `default_headers` or `extra_headers` |
| `403` / `agent_disabled` | Kill switch is on | Re-enable the agent under **Governance → Agents** |
| `429` / `governed_requests_exhausted` | Monthly allowance reached | Check meter (below) or upgrade at [kimss.ai/pricing](https://kimss.ai/pricing) |
| Model not found | Model not vaulted | Vault the provider endpoint + model under **Governance → Connected Infrastructure** |
| Anthropic path errors | `base_url` includes `/v1/messages` | Use `https://api.kimss.ai` only — see [anthropic onboarding](docs/anthropic-onboarding.md) |

**Inspect your monthly cap:**

```bash
curl -s -H "Authorization: Bearer kimss_..." \
  https://api.kimss.ai/api/v1/governed-requests/meter
```

Response shape: [`examples/governed-requests-meter-response.json`](examples/governed-requests-meter-response.json).

Runnable scripts and a local gateway simulator: [kimss-python-quickstart](https://github.com/kimss-ai/kimss-python-quickstart).

---

## What's in this repo

| Path | Purpose |
|------|---------|
| [`openapi/control-plane.yaml`](openapi/control-plane.yaml) | Control-plane REST contract (governed requests, MCP registry, audit, kill switch) |
| [`examples/`](examples/) | MCP RBAC grant and agent governance policy examples |
| [`conformance/`](conformance/) | Spec grounding tests — paths and schemas match `kimssApi` `origin/main` |
| [`docs/anthropic-onboarding.md`](docs/anthropic-onboarding.md) | Complete Anthropic SDK + env-var onboarding |
| [`AI_INTEGRATION.md`](AI_INTEGRATION.md) | Agent-to-agent integration rules for coding agents |
| [`docs/github-org-conversion.md`](docs/github-org-conversion.md) | GitHub org conversion playbook |
| [`scripts/sync_kimssai_repo_metadata.ps1`](scripts/sync_kimssai_repo_metadata.ps1) | Apply descriptions + topics to public repos |

This spec is **curated and versioned** here. Production disables `/api/openapi.json`; treat this file as the public contract for control-plane integrators.

---

## Control-plane surface (summary)

| Area | Endpoints | Auth |
|------|-----------|------|
| Governed requests | `GET /api/v1/governed-requests/meter` | Any workspace member |
| MCP registry | `GET/POST /api/v1/mcp-servers`, grants under `/grants` | Admin for writes |
| Audit log | `POST /audit_log/` | Any workspace member |
| Kill switch | `POST /agent_set_status/` | Workspace member (tier-gated) |
| Agent registry | `POST /v1/agents/register` | API key (`management` scope) |
| Usage events | `POST /v1/usage/events` | API key |
| Telemetry | `GET /api/v1/me/usage`, `/api/v1/telemetry/*` | Any workspace member |

Plans meter **governed requests** (not Kimss credits). Developer tier: 25,000/mo free, hard HTTP 429 with `error=governed_requests_exhausted` at cap.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). SSOT for the live API is `kimssApi` (`kimss-ai/kimssApi`). Update this spec when control-plane routes change on `main`.

- Security: [SECURITY.md](SECURITY.md)
- Code of conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## License

MIT — see [LICENSE](LICENSE).
