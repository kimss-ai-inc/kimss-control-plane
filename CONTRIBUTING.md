# Contributing

## Source of truth

The live Kimss API is implemented in **`kimssApi`** (`kimssai/kimssApi`, `src/app.py` + `kimssapi_functions/`). This repo is a **public contract mirror** — not the runtime.

When you change control-plane routes or request/response shapes in kimssApi:

1. Update `openapi/control-plane.yaml` in the same change window.
2. Extend `conformance/test_spec_grounding.py` if you add paths or required fields.
3. Bump `info.version` in the OpenAPI file.

## Verify locally

```bash
pip install pyyaml pytest
pytest conformance/
```

## Do not

- Invent endpoints that are not deployed at `https://api.kimss.ai`.
- Publish decrypted MCP credentials or real API keys in examples.
