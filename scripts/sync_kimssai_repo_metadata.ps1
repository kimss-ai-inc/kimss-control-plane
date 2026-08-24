#Requires -Version 7.0
<#
.SYNOPSIS
  Apply descriptions, topics, and housekeeping to public kimssai/* GitHub repos.

.DESCRIPTION
  Requires GitHub CLI (`gh`) authenticated with admin access to kimssai repos.
  Run: gh auth login

  Does NOT rename repos. Archives the stray home-assignment repo when -ArchiveStray is set.

.EXAMPLE
  .\sync_kimssai_repo_metadata.ps1
  .\sync_kimssai_repo_metadata.ps1 -ArchiveStray
#>
param(
    [string] $Owner = "kimssai",
    [switch] $ArchiveStray,
    [switch] $DryRun
)

$ErrorActionPreference = "Stop"

$sharedTopics = @(
    "ai-gateway",
    "llm-security",
    "mcp",
    "ai-agents",
    "enterprise-ai",
    "zero-trust",
    "api-gateway",
    "governance"
)

$repos = @{
    "kimss-python-sdk" = @{
        Description = "Official Kimss Python control-plane SDK (PyPI: kimss). Register agents, report usage, MCP helpers. Inference: OpenAI-compatible base_url at api.kimss.ai."
        Topics = $sharedTopics + @("python", "sdk", "pypi", "openai-compatible")
    }
    "kimss-python-quickstart" = @{
        Description = "5-minute AI gateway quickstart for Python — route OpenAI and Anthropic SDK traffic through identity, audit, policy, and kill-switch controls with a one-line change."
        Topics = $sharedTopics + @("python", "quickstart", "openai", "anthropic", "tutorial")
    }
    "kimss-java-sdk" = @{
        Description = "Official Kimss Java SDK (Maven: com.kimss:kimss-java). Control-plane client mirrored from kimssApi — do not edit main as SSOT."
        Topics = $sharedTopics + @("java", "sdk", "maven")
    }
    "kimss-control-plane" = @{
        Description = "Public hub for the Kimss Secure Enterprise Agent Control Plane — OpenAPI spec, MCP RBAC examples, conformance tests."
        Topics = $sharedTopics + @("openapi", "control-plane", "spec")
    }
}

Write-Host "Owner: $Owner" -ForegroundColor Cyan
if (-not $DryRun) {
    gh auth status 2>&1 | Out-Host
}

foreach ($name in $repos.Keys) {
    $cfg = $repos[$name]
    Write-Host "`n== $Owner/$name ==" -ForegroundColor Green

  if ($DryRun) {
        Write-Host "  description: $($cfg.Description)"
        Write-Host "  topics: $($cfg.Topics -join ', ')"
        continue
    }

    gh api "repos/$Owner/$name" -X PATCH `
        -f description="$($cfg.Description)" 2>&1 | Out-Null

    $topicFile = Join-Path $env:TEMP "kimss-topics-$name.json"
    @{ names = $cfg.Topics } | ConvertTo-Json -Compress | Set-Content -Path $topicFile -Encoding utf8NoBOM
    gh api "repos/$Owner/$name/topics" -X PUT `
        -H "Accept: application/vnd.github+json" `
        --input $topicFile 2>&1 | Out-Null
    Remove-Item -Force $topicFile -ErrorAction SilentlyContinue

    Write-Host "  updated description + topics" -ForegroundColor DarkGray
}

if ($ArchiveStray) {
    $stray = "data-engineering-home-assignment"
    Write-Host "`n== Archive $Owner/$stray ==" -ForegroundColor Yellow
    if ($DryRun) {
        Write-Host "[dry-run] would archive $stray"
    } else {
        gh api "repos/$Owner/$stray" -X PATCH -f archived=true 2>&1 | Out-Null
        Write-Host "  archived" -ForegroundColor DarkGray
    }
}

Write-Host "`nDone." -ForegroundColor Cyan
