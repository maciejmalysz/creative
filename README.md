# creative

Automation for submitting creative work to the Cisco **Creative Work Tool**
(`https://cxpp-external-proxy-alln.cisco.com/creative-work-tool/`) under the
Polish Employee Creative Work & Copyright procedure
([KB0066779](https://cisco.service-now.com/helpzone?id=kb_article&sysparm_article=KB0066779)).

> **Status**: Design + working scripts. Production submission validated end-to-end with
> a real cookie/CSRF, both for manual entries and GitHub PR import.

---

## Documentation

- **[Usage Guide](docs/USAGE.md)** — step-by-step instructions for both submission paths (Path A manual + Path B GitHub PR import), prerequisites, troubleshooting, security notes
- **[Design Document](docs/DESIGN.md)** — full design, decision matrix, threat model
- **[API Reference](docs/api-reference.md)** — endpoints, fields, CSRF handling, dropdown values

---

## Two submission paths

The tool itself supports **both** options natively. This repo wraps each path so
it can be driven from an OpenCode skill, a script, or a CI hook.

| Path | When to use | What this repo provides |
|------|-------------|-------------------------|
| **A. Manual submission** (`POST /creative-work-add`) | One-off creative work that is *not* a GitHub PR (docs, presentations, internal pages, designs) | `scripts/submit_creative_work.py` + `creative-work-submit` skill |
| **B. GitHub PR import** (`POST /creative-work-github-add`) | Engineering work delivered as merged PRs on github.com or wwwin-github | `scripts/list_github_prs.py` to preview, plus PR-template + label workflow so the tool picks up only the right PRs |

Both paths require an active **Duo SSO session** to the proxy. Path B *also*
requires a fine-grained GitHub PAT stored once in your tool profile
(`Settings → GitHub → PAT`), or the in-tool GitHub OAuth flow.

See [`docs/DESIGN.md`](docs/DESIGN.md) for the full design and
[`docs/api-reference.md`](docs/api-reference.md) for endpoints, fields, and CSRF
handling.

---

## Quick start

### Path A — manual submission via script

```bash
# 1. One-time: capture session cookie + CSRF from your authenticated browser
#    (the helper script tells you exactly what to grab)
python3 scripts/submit_creative_work.py --capture-help

# 2. Export the values
export CWT_COOKIE="SESSION=…; ITDC_…=…"
export CWT_CSRF="fa38c8ee-f474-44cc-88fa-09298a459867"

# 3. Submit
python3 scripts/submit_creative_work.py \
    --title "NSO Service Pack v2 design doc" \
    --url   "https://wwwin-github.cisco.com/mmalysz/nso-svc/blob/main/docs/v2.md" \
    --org   "CX" \
    --team  "CX EMEA" \
    --manager "Imie Nazwisko" \
    --job   "Customer Delivery Architect" \
    --deliverable "Design Document"
```

### Path B — GitHub PR import

1. In the tool: **Profile → GitHub** → paste a fine-grained PAT
   (`https://github.com/settings/tokens?type=beta` — read access to PRs is enough).
2. On the dashboard: click **Import from GitHub**. The tool fetches all
   *closed/merged* PRs since the **26th of the previous month** for repos the PAT
   can see.
3. Tick the PRs that count as creative work, accept the statement, **Save**.

To pre-flight what the tool will see:

```bash
export GH_TOKEN="github_pat_…"           # fine-grained PAT
python3 scripts/list_github_prs.py --since-26th
```

---

## Repository layout

```
creative/
├── README.md
├── docs/
│   ├── DESIGN.md            # full design — both paths, decision matrix, threat model
│   └── api-reference.md     # endpoints, fields, CSRF, cookies, dropdowns
├── skills/
│   └── creative-work-submit/
│       └── SKILL.md         # OpenCode skill — drives both paths
├── scripts/
│   ├── submit_creative_work.py   # Path A — direct POST
│   └── list_github_prs.py        # Path B — preview PRs that would be imported
├── .github/
│   └── pull_request_template.md  # PR title/body conventions for clean import
└── project_notes/                # session notes (kept out of distributed builds)
```

> The auto-label workflow (`.github/workflows/creative-work-tag.yml`) is staged
> at `/tmp/cwt-workflow.yml` but not committed — adding it requires refreshing
> the gh CLI token with the `workflow` scope:
> `gh auth refresh -h github.com -s workflow` then `git add` and push.

---

## Why not a full MCP server?

Considered and rejected for v1 — see [`docs/DESIGN.md`](docs/DESIGN.md#decision-skill--scripts-vs-mcp-server)
for the trade-offs. Short version: the tool already exposes a usable POST API
and a built-in GitHub importer. A skill + two small scripts cover 100% of the
workflow at a fraction of the maintenance cost. An MCP server stays on the
roadmap if multiple Polish CX engineers want to share one Cookie/CSRF refresh
service.

---

## Support

Tool support: `itdcsupport@cisco.com`
Procedure questions: HelpZone → Pay Inquiry → "creative work"
