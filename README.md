# Kimss Control Plane

Public hub for the **Kimss Secure Enterprise Agent Control Plane** — a model-agnostic API gateway for enterprise AI agents.

Kimss is not a chat platform. Customers bring their own agents, models, and infrastructure. Kimss provides registry, SSO identity mapping, MCP RBAC, governed-request metering, gateway-verified audit (Article 12 path), and an authoritative kill switch at the gateway.

**Live API:** `https://api.kimss.ai`

## Start here

| Goal | Repo |
|------|------|
| Route OpenAI / Anthropic traffic through Kimss in 5 minutes | [kimss-python-quickstart](https://github.com/kimss-ai-inc/kimss-python-quickstart) |
| Python control-plane SDK (`pip install kimss`) | [kimss-python-sdk](https://github.com/kimss-ai-inc/kimss-python-sdk) |
| Java control-plane SDK (Maven `com.kimss:kimss-java`) | [kimss-java-sdk](https://github.com/kimss-ai-inc/kimss-java-sdk) |
| Product docs & trust center | [kimss.ai](https://kimss.ai) |

### Inference (no Kimss package required)

Point your existing SDK at Kimss with a one-line `base_url` change:

```python
from openai import OpenAI

client = OpenAI(
    api_key="kimss_...",
    base_url="https://api.kimss.ai/v1",
    default_headers={"X-Kimss-Agent-Id": "my-agent"},
)
```

Anthropic: `base_url="https://api.kimss.ai"` (SDK appends `/v1/messages`).

Auth: `Authorization: Bearer kimss_...`, `X-Kimss-Key`, or `x-api-key: kimss_...`.

## What's in this repo

| Path | Purpose |
|------|---------|
| [`openapi/control-plane.yaml`](openapi/control-plane.yaml) | Control-plane REST contract (governed requests, MCP registry, audit, kill switch) |
| [`examples/`](examples/) | MCP RBAC grant and agent governance policy examples |
| [`conformance/`](conformance/) | Spec grounding tests — paths and schemas match `kimssApi` `origin/main` |
| [`docs/github-org-conversion.md`](docs/github-org-conversion.md) | Plan to convert `kimssai` User → Organization |
| [`scripts/sync_kimssai_repo_metadata.ps1`](scripts/sync_kimssai_repo_metadata.ps1) | Apply descriptions + topics to public `kimssai/*` repos |

This spec is **curated and versioned** here. Production disables `/api/openapi.json`; treat this file as the public contract for control-plane integrators.

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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). SSOT for the live API is `kimssApi` (`kimss-ai-inc/kimssApi`). Update this spec when control-plane routes change on `main`.

## License

MIT — see [LICENSE](LICENSE).
