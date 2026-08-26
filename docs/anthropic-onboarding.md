# Anthropic onboarding — route Claude through Kimss

Kimss exposes a **dual-listener gateway**: OpenAI-compatible chat at `/v1/chat/completions` and Anthropic Messages at `/v1/messages`. Your Anthropic SDK stays native — change `base_url`, swap the API key, and add Agent-Id headers.

**Live gateway:** `https://api.kimss.ai`

## Before → After

**Before** — call Anthropic directly:

```python
from anthropic import Anthropic

client = Anthropic(api_key=ANTHROPIC_API_KEY)
```

**After** — route through Kimss (one-line `base_url` change):

```python
import os
from anthropic import Anthropic

client = Anthropic(
    api_key=os.getenv("KIMSS_WORKSPACE_KEY") or os.getenv("KIMSS_API_KEY"),
    base_url="https://api.kimss.ai",
    default_headers={
        "X-Kimss-Agent-Id": os.getenv("KIMSS_AGENT_ID", "my_agent"),
        "X-Kimss-Agent-Name": os.getenv("KIMSS_AGENT_NAME", "My Agent"),
    },
)
resp = client.messages.create(
    model=os.getenv("KIMSS_MODEL", "custom:your-vaulted-model"),
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello via Kimss"}],
)
```

The Anthropic SDK appends `/v1/messages` to `base_url`. Do **not** include `/v1/messages` in `base_url`.

## Zero-code environment variables

For apps that read Anthropic env vars without code changes:

```bash
ANTHROPIC_BASE_URL="https://api.kimss.ai"
ANTHROPIC_API_KEY="kimss_your_kimss_key"
```

Also set `X-Kimss-Agent-Id` via your app's header injection or SDK `default_headers` — the gateway requires agent attribution on every governed request.

OpenAI apps use the parallel pattern:

```bash
OPENAI_BASE_URL="https://api.kimss.ai/v1"
OPENAI_API_KEY="kimss_your_kimss_key"
```

## 3-step setup (real gateway)

### 1. Sign in and vault

[Create Free Account →](https://kimss.ai/app/signup). Open **Governance → Connected Infrastructure** and vault your Anthropic endpoint + key.

Developer tier (Always Free): 25,000 governed requests/month, 14-day telemetry, up to 5 workspace members. No credit card.

### 2. Mint key

**Gateway → Generate Key**. Copy `kimss_...`. Register or note your `agent_id` under Gateway.

### 3. Route traffic

```bash
git clone https://github.com/kimss-ai/kimss-python-quickstart.git
cd kimss-python-quickstart
pip install -r requirements.txt
cp .env.example .env   # KIMSS_API_KEY, KIMSS_AGENT_ID, KIMSS_MODEL
```

Adapt the Anthropic snippet above, or run the OpenAI quickstart first — the gateway contract is identical aside from listener URL and SDK.

Open **Gateway → Recent calls** to see the governed audit trail.

## Authentication options

Kimss accepts any of these on inference requests:

| Header | Example |
|--------|---------|
| `Authorization` | `Bearer kimss_...` |
| `X-Kimss-Key` | `kimss_...` |
| `x-api-key` | `kimss_...` |

## Enforcement responses

| HTTP | Code | Meaning |
|------|------|---------|
| `403` | `agent_disabled` | Kill switch is on — re-enable under **Governance → Agents** |
| `429` | `governed_requests_exhausted` | Monthly allowance reached — check meter or upgrade at [kimss.ai/pricing](https://kimss.ai/pricing) |

Inspect your cap programmatically:

```bash
curl -s -H "Authorization: Bearer kimss_..." \
  https://api.kimss.ai/api/v1/governed-requests/meter
```

See [`examples/governed-requests-meter-response.json`](../examples/governed-requests-meter-response.json) for the response shape.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `401` / invalid API key | Wrong or missing `kimss_...` key | Mint a new key under **Gateway → Generate Key** |
| `400` / missing agent | No `X-Kimss-Agent-Id` header | Set `KIMSS_AGENT_ID` and pass via `default_headers` |
| `403` / `agent_disabled` | Kill switch is on | Re-enable the agent under **Governance → Agents** |
| `429` / `governed_requests_exhausted` | Monthly allowance reached | Wait for reset or upgrade at [kimss.ai/pricing](https://kimss.ai/pricing) |
| Model not found | Model not vaulted | Vault Anthropic under **Governance → Connected Infrastructure** |
| Wrong endpoint | `base_url` includes `/v1/messages` | Use `https://api.kimss.ai` only — SDK adds the path |

## Related

- Runnable Python tutorial: [kimss-python-quickstart](https://github.com/kimss-ai/kimss-python-quickstart)
- Agent-to-agent rules: [AI_INTEGRATION.md](../AI_INTEGRATION.md)
- Control-plane spec: [openapi/control-plane.yaml](../openapi/control-plane.yaml)
- Hub README: [README.md](../README.md)
