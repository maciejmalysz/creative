# creative

**Automation for submitting creative work to the Cisco Creative Work Tool** — talk to your AI assistant to submit entries under the Polish Employee Creative Work & Copyright procedure ([KB0066779](https://cisco.service-now.com/helpzone?id=kb_article&sysparm_article=KB0066779)).

---

## Two ways to submit

| | Direct submission | GitHub PR import |
|--|--|--|
| **Use when** | Documents, presentations, recordings, designs — anything that's not a GitHub PR | Code, scripts, automation, IaC, MCP servers — engineering work delivered as merged PRs |
| **Deliverable location** | SharePoint, Box, Webex, Confluence (must be Cisco-trusted URL) | github.com or wwwin-github.cisco.com (merged or closed PR) |
| **How to submit** | Tell your AI: "Submit creative work for [title]. Source is [URL]. Upload to SharePoint and submit as [deliverable type]." | Tell your AI: "I merged PR #X in [repo]. Submit it as creative work." |

Both paths require the **`creative-work-submit` skill** installed in your AI assistant (OpenCode / Claude Code / Cursor).

---

## Quickstart

### 1. Install the skill

Copy `skills/creative-work-submit/` to your AI assistant's skill directory:

```bash
# OpenCode
cp -r skills/creative-work-submit ~/.config/opencode/skills/

# Claude Code / Cursor
cp -r skills/creative-work-submit ~/.claude/skills/
```

### 2. Talk to your AI

**Example 1 — Submit a design document from Confluence:**

> "Submit a Creative Work entry for the Fabric Rollout Automation SRD. The source is the Confluence page at https://scdp.cisco.com/conf/spaces/TSPP/pages/439268357/Fabric+Rollout+Automation+-+SRD — render it to PDF, upload to my SharePoint submissions folder under `mmalysz-creative-work/<yearmonth>/`, then submit it as a 'Requirements gathering and design preparation' deliverable."

**What the AI does:**
- Renders the Confluence page to PDF (via CDP browser automation)
- Uploads to your SharePoint submissions folder
- Submits the Creative Work Tool form with the SharePoint URL

**Example 2 — Import a merged GitHub PR:**

> "I just merged PR #1 in maciejmalysz/creative on github.com. Submit it as a Creative Work entry — title should stay as the PR title, deliverable URL should be the PR URL, and use my default deliverable type."

**What the AI does:**
- Opens the Creative Work Tool in a browser (with your SSO session)
- Clicks "Import from GitHub"
- Selects your PR, accepts the terms, and imports it

---

## Documentation

Full user guide: **[docs/USAGE.md](https://wwwin-github.cisco.com/pages/mmalysz/creative/USAGE.html)** (GitHub Pages)

Covers:
- When to use each submission path
- How to formulate your AI prompt
- Deliverable type cheat sheet
- Troubleshooting

---

## For developers

<details>
<summary>Scripts, API reference, and design docs</summary>

### Repository layout

```
creative/
├── README.md
├── docs/
│   ├── USAGE.md             # End-user guide (rendered to GitHub Pages)
│   ├── DESIGN.md            # Full design — both paths, decision matrix, threat model
│   └── api-reference.md     # Endpoints, fields, CSRF, cookies, dropdowns
├── skills/
│   └── creative-work-submit/
│       └── SKILL.md         # OpenCode skill — drives both paths
├── scripts/
│   ├── submit_creative_work.py   # Path A — direct POST
│   └── list_github_prs.py        # Path B — preview PRs that would be imported
└── .github/
    └── pull_request_template.md  # PR title/body conventions for clean import
```

### Direct script usage (Path A)

```bash
# 1. Capture session cookie + CSRF from your authenticated browser
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

### GitHub PR pre-flight (Path B)

```bash
export GH_TOKEN="github_pat_…"           # fine-grained PAT
python3 scripts/list_github_prs.py --since-26th

# For Cisco internal GitHub:
python3 scripts/list_github_prs.py --host wwwin-github.cisco.com --since-26th
```

### Why not a full MCP server?

Considered and rejected for v1 — see [`docs/DESIGN.md`](docs/DESIGN.md#decision-skill--scripts-vs-mcp-server) for the trade-offs. Short version: the tool already exposes a usable POST API and a built-in GitHub importer. A skill + two small scripts cover 100% of the workflow at a fraction of the maintenance cost.

</details>

---

## Support

- **Tool support**: `itdcsupport@cisco.com`
- **Procedure questions**: HelpZone → Pay Inquiry → "creative work"
- **Repo issues**: https://github.com/maciejmalysz/creative/issues
