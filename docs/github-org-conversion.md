# Kimss `kimssai` GitHub User → Organization conversion

**Status:** pre-work complete — ready for account transform  
**Account:** [github.com/kimssai](https://github.com/kimssai) (GitHub **User**, created 2015)  
**Target:** GitHub **Organization** with the same visible name `kimssai`

## Pick up tomorrow (2026-08-26)

Clone this repo on the machine where you will sign in as `kimssai`:

```bash
git clone https://github.com/kimssai/kimss-control-plane.git
```

### Already done (2026-08-25)

- [x] Published [kimssai/kimss-control-plane](https://github.com/kimssai/kimss-control-plane) (OpenAPI, examples, conformance tests)
- [x] Descriptions + discovery topics on all four product repos (`scripts/sync_kimssai_repo_metadata.ps1`)
- [x] Archived `data-engineering-home-assignment`
- [x] Vault note: `kimss-docs` → `architecture/kimss-public-repos.md`

### Your steps tomorrow

1. Sign in to GitHub as **`kimssai`** (password + 2FA).
2. Settings → Account → **Transform account** (if offered). See [Option A](#option-a--convert-user-to-org-if-eligible) below.
3. If no transform UI: follow [Option B](#option-b--new-org--transfer-most-common).
4. After transform/transfer, re-wire `kimssApi` secrets:
   - `KIMSS_SDK_MIRROR_PAT`, `KIMSS_SDK_MIRROR_REPO`
   - `KIMSS_JAVA_SDK_MIRROR_REPO`, `KIMSS_JAVA_SDK_MIRROR_SSH_KEY`, `KIMSS_JAVA_SDK_WORKFLOW_PAT`
5. Dry-run mirror: push a no-op to `kimssApi/kimss_sdk/` or trigger `mirror_kimss_sdk.yml` manually.
6. Verify PyPI package homepage still resolves to `kimssai/kimss-python-sdk`.
7. Re-run Scorecard / bestpractices.dev if repo URLs changed.

Auth on this machine uses the `kimssai` OAuth token in Windows Credential Manager (`git:https://github.com`). On the other computer, use `gh auth login` as `kimssai` or the same credential flow.

## Why convert

| User account today | Organization |
|--------------------|--------------|
| Reads as a personal account | Reads as a company/vendor |
| No org-level SSO for repo access | Enterprise SSO + SAML for members |
| Limited team RBAC | Teams, custom roles, org security policies |
| Mixed credibility (e.g. unrelated public repos) | Cleaner separation of product vs personal |

Public repos (`kimss-python-sdk`, `kimss-python-quickstart`, `kimss-java-sdk`, `kimss-control-plane`) should live under an **Organization** before enterprise security reviews.

## Preconditions

1. **Owner access** to the `kimssai` user account (password + 2FA).
2. **No blocking billing** on the account (orgs need a billing manager if using paid features).
3. **Inventory** of everything owned by `kimssai`:
   - Public repos (four product repos — see inventory below)
   - Deploy keys, PATs, OAuth apps, GitHub Apps
   - PyPI trusted publisher linkage (`kimss` → `kimssai/kimss-python-sdk`)
   - Maven Central / Sonatype namespace (`com.kimss`)
   - OpenSSF Scorecard / bestpractices.dev project URLs
   - Cursor Marketplace plugin repo references
4. **Quiet window** — mirror workflows from `kimssApi` force-push public SDK repos; schedule conversion outside deploy windows.

## Recommended path (GitHub-supported)

GitHub does **not** rename a User into an Org in place. Standard approach:

### Option A — Convert user to org (if eligible)

GitHub occasionally offers **account conversion** for eligible accounts:

1. Sign in as `kimssai`.
2. Settings → Account → **Transform account** (only if the UI offers it).
3. Follow GitHub’s wizard: create org, transfer repos, reassign billing.

If the transform option is unavailable, use Option B.

### Option B — New org + transfer (most common)

1. Create organization `kimssai` **only if the name is free** — if the user holds the name, you must first:
   - Rename user `kimssai` → e.g. `kimssai-bot` or `kimssai-owner`, **or**
   - Use org name `kimss-ai` temporarily then rename after user deletion (risky).
   - **Preferred:** GitHub account conversion (Option A) to keep the `kimssai` slug.

2. Create org with SSO-ready settings:
   - Require 2FA for all members
   - Base permissions: none
   - Disable forking for private repos (if any added later)

3. **Transfer repositories** (Settings → General → Transfer):
   - `kimss-python-sdk`
   - `kimss-python-quickstart`
   - `kimss-java-sdk`
   - `kimss-control-plane`
   - Archive or privatize `data-engineering-home-assignment` **before** transfer (or archive immediately after).

4. **Re-wire automation:**
   | Integration | Update |
   |-------------|--------|
   | `kimssApi` mirror workflows | `KIMSS_PYTHON_SDK_MIRROR_REPO`, Java mirror secrets |
   | PyPI trusted publisher | GitHub repo path after transfer (usually unchanged if org name matches) |
   | OpenSSF Scorecard | Re-register project URL if slug changes |
   | `bestpractices.dev` | Update repo link |
   | Docs / README links | `github.com/kimssai/*` (same if org keeps name) |

5. **Teams**
   - `engineering` — write on SDK + control-plane repos
   - `bots` — machine users for mirror deploy keys only
   - `marketing` — read + issues on quickstart only

6. **Verify**
   - Force-push mirror dry-run on a test branch
   - `pip install kimss` still resolves PyPI metadata URLs
   - Scorecard badge still resolves

## What does NOT move automatically

- Stars and watchers (transfer preserves stars on the repo)
- Personal gists on the user account
- GitHub Pages custom domains (re-verify DNS)
- Webhooks pointing at `repos/kimssai-user/...` paths

## Rollback

Keep the old user account as `kimssai-archive` with **no repos** for 90 days so PATs and deploy keys can be traced if something still points at the user namespace.

## Timeline suggestion

| Week | Action |
|------|--------|
| 1 | Archive stray repos; fix descriptions/topics (`scripts/sync_kimssai_repo_metadata.ps1`) |
| 1 | Publish `kimss-control-plane`; link from SDK READMEs |
| 2 | Attempt GitHub account transform OR rename user + create org |
| 2 | Transfer repos; update kimssApi secrets |
| 3 | Re-run mirror workflows; verify PyPI + Scorecard |
| 4 | Enable org 2FA policy; invite team |

## Decision log

- **Do not** rename `kimss-python-quickstart` → `kimss-control-plane` (different audiences; keep quickstart for developer SEO).
- **Do** use `kimss-control-plane` as the OpenAPI + policy hub (this repo).
