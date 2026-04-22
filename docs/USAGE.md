# Creative Work Tool — User Guide

**Audience**: Cisco engineers with the `creative-work-submit` skill installed in their AI assistant (OpenCode / Claude Code / Cursor).

**What this guide covers**: How to talk to your AI assistant to submit creative work entries — not how to run Python scripts directly.

---

## Assumptions

You have:
- The `creative-work-submit` skill installed in your AI assistant
- An active Duo SSO session to `cxpp-external-proxy-alln.cisco.com` (the Creative Work Tool)
- CDP browser automation available (your AI can control Chrome with your real cookies)

If you're missing any of these, see the [Installation](#installation) section below.

---

## The two submission options

The Creative Work Tool supports two native submission paths. This guide shows you how to use each via conversational prompts to your AI assistant.

### Option A — Direct submission

**Use when**: Your deliverable is a **document, presentation, recording, design, or any artifact** that already exists somewhere (SharePoint, Box, Webex recording, Confluence page).

**Requirements**:
- The deliverable must be at a **Cisco-trusted URL** (cisco.sharepoint.com, box.com, webex.com, etc.)
- Personal SharePoint URLs and public links are rejected by the tool

**What the AI handles**:
1. Rendering or exporting the source (e.g., Confluence page → PDF)
2. Uploading to your SharePoint submissions folder
3. Submitting the Creative Work Tool form with the SharePoint URL

### Option B — GitHub PR import

**Use when**: Your deliverable is **code, scripts, automation, IaC, a workflow, an MCP server** — anything that lives in a Git repository and was delivered as a pull request.

**Requirements**:
- PR must be **merged or closed** on either `github.com` or `wwwin-github.cisco.com`
- A GitHub API token (fine-grained PAT) must be configured in your Creative Work Tool profile

**Convention**: PR titles should start with `[creative]` (the auto-label workflow in this repo will tag it; the tool doesn't require this but it makes PRs easy to find later).

**What the AI handles**:
1. Opening the Creative Work Tool in a browser (with your SSO session)
2. Clicking "Import from GitHub"
3. Selecting the PR row, accepting the terms, and clicking "Import Selected"

---

## Comparison table

| | Direct submission | GitHub PR import |
|--|--|--|
| **Best for** | Documents, decks, recordings, designs | Code, IaC, automation, MCP servers |
| **Where deliverable lives** | SharePoint / Box / Webex / Confluence-exported | github.com or wwwin-github.cisco.com |
| **URL constraints** | Must be Cisco-trusted URL (no personal SharePoint, no public links) | Must be a merged/closed PR |
| **Pre-requisites** | None beyond the skill | GitHub API token configured in Creative Work Tool profile |
| **Who fills the form** | You + AI (deliverable type, dates, description) | Tool pre-fills from PR title/body; you confirm |

---

## How to formulate your request to the AI

When asking your AI assistant to submit creative work, include:

- **Source URL or PR reference** — where the deliverable lives
- **Deliverable type** (if not using your default) — see [Deliverable type cheat sheet](#deliverable-type-cheat-sheet)
- **Target SharePoint subfolder** (for direct submissions) — e.g., `mmalysz-creative-work/202604/`
- **Dates** (if not "today") — start date, end date, or both

**Example prompts**:

- "Submit creative work for [title]. Source is [URL]. Upload to SharePoint and submit as [deliverable type]."
- "I merged PR #X in [repo]. Submit it as creative work."
- "Submit the deck at [SharePoint URL] as a 'Knowledge sharing internal: presentations / training' deliverable."

---

## Two worked examples

### Example 1 — Direct submission of an SRD PDF

**User prompt to AI:**

> "Submit a Creative Work entry for the Fabric Rollout Automation SRD. The source is the Confluence page at https://scdp.cisco.com/conf/spaces/TSPP/pages/439268357/Fabric+Rollout+Automation+-+SRD — render it to PDF, upload to my SharePoint submissions folder under `mmalysz-creative-work/<yearmonth>/`, then submit it as a 'Requirements gathering and design preparation' deliverable."

**What the AI does end-to-end:**

1. **Renders the Confluence page to PDF** via CDP `Page.printToPDF` (Confluence's flyingpdf endpoint needs CSRF + a session that bypasses available tokens — the print-to-PDF path is reliable)
2. **Uploads the PDF to SharePoint** at `https://cisco.sharepoint.com/sites/ITDCSubmissions/Shared Documents/Submissions/<cec>/mmalysz-creative-work/<yyyymm>/` via SharePoint REST `_api/web/folders` + `Files/add` (driven from the SharePoint tab in CDP Chrome — uses your real cookies)
3. **Reads the form CSRF + defaults** from the hidden `#creativeWorkModal` on the Creative Work Tool page
4. **POSTs the new entry** via `fetch()` from inside the Creative Work Tool page (200 OK → redirects to calendar)

**What success looks like:**

- The Creative Work Tool calendar at `?year=YYYY&month=M` shows the new entry with status `Pending`
- The SharePoint folder contains the uploaded PDF

### Example 2 — GitHub PR auto-import

**User prompt to AI:**

> "I just merged PR #1 in maciejmalysz/creative on github.com. Submit it as a Creative Work entry — title should stay as the PR title, deliverable URL should be the PR URL, and use my default deliverable type."

**What the AI does end-to-end:**

1. **Opens the Creative Work Tool page** in CDP Chrome (port 9225, finds tab via `cdp-command.py tabs`)
2. **Clicks "Import from GitHub"** → the tool fetches the user's recent merged PRs via the GitHub token in their profile
3. **Locates the PR row** matching the URL/repo → checks its checkbox
4. **Checks the mandatory terms checkbox** (`#githubPrsTermsCheckbox`)
5. **Clicks "Import Selected"** (`#modal-save`) → "Successfully imported 1 GitHub pull request(s)!"

**What success looks like:**

- The Creative Work Tool calendar shows the new entry with the PR title
- The deliverable URL is the PR URL
- Status is `Pending` until manager approval

---

## Deliverable type cheat sheet

When submitting via **direct submission** (Path A), you must specify a deliverable type. The tool's dropdown includes:

- **"Requirements gathering and design preparation"** → SRDs, HLDs, LLDs, design docs, architecture diagrams
- **"Automation and software development: scripting and coding"** → repos, scripts, MCP servers, workflows, automation tools
- **"Knowledge sharing internal: presentations / training"** → decks, videos, demos, training materials
- **"Customer engagement: workshops / consulting"** → workshop materials, consulting deliverables, customer-facing docs

For **GitHub PR import** (Path B), the tool defaults to **"Code Contribution"** (or whatever is set in your profile).

> **Note**: The full dropdown list is dynamic and depends on your org/team selection. See the Creative Work Tool form for the complete list.

---

## Troubleshooting

### "Personal SharePoint URL rejected"

**Symptom**: The tool rejects a SharePoint URL like `https://cisco.sharepoint.com/personal/mmalysz/...`

**Fix**: Upload to the **ITDCSubmissions** site instead. The AI knows the path:
```
https://cisco.sharepoint.com/sites/ITDCSubmissions/Shared Documents/Submissions/<cec>/mmalysz-creative-work/<yyyymm>/
```

Tell your AI: "Upload to ITDCSubmissions under my creative work folder."

### "GitHub PR not appearing in import dialog"

**Symptom**: You merged a PR but it doesn't show up when you click "Import from GitHub" in the tool.

**Fix**:
1. Confirm you have a GitHub API token configured in your Creative Work Tool profile (`Settings → GitHub → PAT`)
2. Reload the Creative Work Tool page (the PR list is fetched on page load)
3. Verify the PR is **merged or closed** (not just open)
4. Verify you are the PR **author** (the tool filters on `author:@me`)

### "PR import shows 'no PRs found'"

**Symptom**: The "Import from GitHub" dialog is empty even though you have merged PRs.

**Fix**: The tool only fetches PRs **since the 26th of the previous month** (matches the Polish payroll cutoff). If your PR was merged before that date, it won't appear. You can still submit it via **direct submission** (Path A) using the PR URL.

### "Form POST returns 403"

**Symptom**: The AI reports a 403 error when submitting the form.

**Fix**: The CSRF token has expired. Reload the Creative Work Tool page in your browser and let the AI re-read the form. CSRF tokens are issued per page load and expire after ~8–10 hours.

### "Duo session expired"

**Symptom**: The AI reports a redirect to `sso.duosecurity.com` when trying to access the Creative Work Tool.

**Fix**: Your Duo SSO session has expired. Open the Creative Work Tool in your browser, complete the Duo challenge, then retry the AI submission.

---

## Installation

### 1. Install the skill

Copy the skill to your AI assistant's skill directory:

```bash
# OpenCode
cp -r skills/creative-work-submit ~/.config/opencode/skills/

# Claude Code / Cursor
cp -r skills/creative-work-submit ~/.claude/skills/
```

### 2. Verify CDP browser automation

The skill uses CDP (Chrome DevTools Protocol) to control your browser with your real cookies. Verify it's available:

```bash
# Check if the cdp-browser-automation skill is installed
ls ~/.config/opencode/skills/cdp-browser-automation/
```

If missing, install it from the `opencode-config` repo or ask your AI: "Install the cdp-browser-automation skill."

### 3. Configure GitHub token (for PR import only)

If you plan to use **GitHub PR import** (Path B):

1. Generate a fine-grained GitHub PAT at https://github.com/settings/tokens?type=beta
   - Scope: **Pull requests: Read**
   - Repositories: Select the repos you want to import PRs from
2. Open the Creative Work Tool at https://cxpp-external-proxy-alln.cisco.com/creative-work-tool/
3. Go to **Settings → GitHub** and paste the PAT

---

## For developers / appendix

### Direct script usage (Path A)

If you prefer to run the Python script directly (without the AI skill):

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

To preview what PRs the tool will see before opening the import dialog:

```bash
export GH_TOKEN="github_pat_…"           # fine-grained PAT
python3 scripts/list_github_prs.py --since-26th

# For Cisco internal GitHub:
python3 scripts/list_github_prs.py --host wwwin-github.cisco.com --since-26th
```

### API reference

Full endpoint documentation, field schemas, and CSRF handling: [`api-reference.md`](api-reference.md)

### Design documentation

Architecture, decision matrix, threat model: [`DESIGN.md`](DESIGN.md)

---

## Support

- **Tool support**: `itdcsupport@cisco.com`
- **Procedure questions**: HelpZone → Pay Inquiry → "creative work"
- **Repo issues**: https://github.com/maciejmalysz/creative/issues
