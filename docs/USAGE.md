# Creative Work Tool — Usage Guide

**Version**: 1.0
**Last updated**: 2026-04-22
**Target system**: `https://cxpp-external-proxy-alln.cisco.com/creative-work-tool/` (v1.0.23-SNAPSHOT)
**Procedure**: KB0066779 — Employee creative work and copyrights salary – Poland

---

## 1. Overview

This toolkit automates submission of creative work to the Cisco Creative Work Tool under the Polish creative work and copyright payroll procedure. The tool itself supports two native submission paths:

| Path | Use Case | What You Submit |
|------|----------|-----------------|
| **Path A — Manual Direct Submission** | One-off creative work that is *not* a GitHub PR: documentation, presentations, internal pages, designs, recordings | Title + link + metadata via `scripts/submit_creative_work.py` |
| **Path B — GitHub PR-Based Submission** | Engineering work delivered as merged pull requests on github.com or wwwin-github.cisco.com | Bulk import of closed/merged PRs via the tool's built-in GitHub integration |

Both paths require an active **Duo SSO session** to the Creative Work Tool proxy. Path B additionally requires a GitHub Personal Access Token (PAT) or OAuth connection configured in the tool.

**When to use which path:**
- Use **Path A** for standalone deliverables: design documents, architecture diagrams, customer presentations, internal wiki pages, training materials.
- Use **Path B** for code contributions, bug fixes, feature implementations, documentation PRs — anything delivered as a GitHub pull request.
- Use **both** if you have a mix: run Path B first to import all eligible PRs, then Path A for non-PR items.

---

## 2. Prerequisites

### 2.1 Network Access

- **Cisco VPN or on-premises network** — the Creative Work Tool proxy (`cxpp-external-proxy-alln.cisco.com`) is only accessible from Cisco internal networks.
- **Duo SSO enrollment** — you must be enrolled in Duo and able to complete push/SMS challenges.

### 2.2 Software

- **Python 3.7+** — both scripts use only standard library modules (`urllib`, `json`, `argparse`, `datetime`). No `pip install` required.
- **Git** (optional) — for cloning this repository and for Path B pre-flight checks.
- **GitHub CLI (`gh`)** (optional) — for Path B pre-flight if you prefer `gh pr list` over the Python script.

### 2.3 Browser

- **Chrome, Firefox, or Safari** — for capturing session cookies and CSRF tokens (Path A) and for using the tool's GitHub import UI (Path B).

### 2.4 Credentials

- **Path A**: Session cookie + CSRF token from your authenticated browser session (captured once per Duo session, typically valid 8–10 hours).
- **Path B**: GitHub Personal Access Token (fine-grained, read-only, scoped to your repositories) **or** GitHub OAuth connection via the tool's built-in flow.

---

## 3. Path A — Manual Direct Submission

Use this path when you have a single piece of creative work that is **not** a GitHub PR: a design document, a presentation, an internal wiki page, a recording, etc.

### 3.1 Install the Skill (Optional)

If you use OpenCode or Claude Code with the `creative-work-submit` skill:

```bash
# Skill is already in this repo at skills/creative-work-submit/SKILL.md
# If you cloned the repo, the skill is available automatically
```

The skill wraps the steps below and can be invoked by saying "submit creative work" in your AI assistant session.

### 3.2 Capture Session Cookie and CSRF Token

The Creative Work Tool uses **Duo SSO** and **CSRF protection**. You must capture both from your authenticated browser session.

**Steps:**

1. Open `https://cxpp-external-proxy-alln.cisco.com/creative-work-tool/` in Chrome.
2. Complete the Duo SSO challenge (push notification or SMS code).
3. Once you see the dashboard, open **Chrome DevTools** (F12 or Cmd+Option+I).
4. **Capture the session cookie:**
   - Go to **Application** → **Cookies** → `https://cxpp-external-proxy-alln.cisco.com`
   - You will see one or more cookies (typically `SESSION=…` and `ITDC_…=…`).
   - Right-click any cookie → **Copy** → **Copy as cURL** (this gives you the full cookie header).
   - Alternatively, manually copy each cookie as `NAME1=VALUE1; NAME2=VALUE2; …`
   - Example: `SESSION=abc123def456; ITDC_AUTH=xyz789`
5. **Capture the CSRF token:**
   - Go to **Elements** tab in DevTools.
   - Press **Ctrl+F** (or Cmd+F) and search for `_csrf`.
   - You will find a hidden input like `<input type="hidden" name="_csrf" value="fa38c8ee-f474-44cc-88fa-09298a459867">`.
   - Copy the `value` attribute (the UUID string).
6. **Export both as environment variables:**
   ```bash
   export CWT_COOKIE='SESSION=abc123def456; ITDC_AUTH=xyz789'
   export CWT_CSRF='fa38c8ee-f474-44cc-88fa-09298a459867'
   ```

**Tip:** Run the helper command to see these instructions again:

```bash
python3 scripts/submit_creative_work.py --capture-help
```

**Session lifetime:** The Duo session typically lasts 8–10 hours. When you get an HTTP 302 redirect to `sso.duosecurity.com` or an HTTP 403 error, repeat the capture steps.

### 3.3 Capture Dropdown Values

The Creative Work Tool uses cascading dropdowns for organization, team, manager, job title, and deliverable type. These values are **dynamic** and must match exactly what the tool expects.

**Option 1: Read from the tool UI**

1. In the Creative Work Tool dashboard, click **Report Creative Work**.
2. In the modal, select your organization from the dropdown.
3. The team, manager, job title, and deliverable dropdowns will populate automatically.
4. Note down the exact text of each value you select.

**Option 2: Dump all dropdown values via JavaScript**

Open the tool dashboard, open the **Report Creative Work** modal, select your organization, then run this in the **DevTools Console**:

```javascript
copy(JSON.stringify({
  org: [...document.querySelectorAll('#organizationNameReportCreativeWork option')].map(o => o.value),
  team: [...document.querySelectorAll('#teamNameReportCreativeWork option')].map(o => o.value),
  manager: [...document.querySelectorAll('#managerNameReportCreativeWork option')].map(o => o.value),
  job: [...document.querySelectorAll('#jobTitleReportCreativeWork option')].map(o => o.value),
  deliverable: [...document.querySelectorAll('#deliverableNameReportCreativeWork option')].map(o => o.value),
}, null, 2));
```

This copies a JSON object to your clipboard. Save it to `~/.config/creative-work-tool/dropdowns.json` for future reference.

**Common values (as of 2026-04-22):**

- **Organization**: `CX`, `Engineering, Enterprise Connectivity & Collaboration`, `Sales`, `Splunk Customer Success & Experience`, etc.
- **Team** (for CX): `CX EMEA`, `CX Americas`, `CX APJ`, etc.
- **Deliverable** (for CX EMEA): `Design Document`, `Code Contribution`, `Presentation`, `Training Material`, `Internal Tool`, etc.

See [`docs/api-reference.md`](api-reference.md) for the full list captured on 2026-04-22.

### 3.4 Create a `.env` Template (Optional)

To avoid typing the same values every time, create a `.env` file in the project root:

```bash
# .env — DO NOT COMMIT THIS FILE
export CWT_COOKIE='SESSION=…; ITDC_AUTH=…'
export CWT_CSRF='fa38c8ee-f474-44cc-88fa-09298a459867'
export CWT_ORG='CX'
export CWT_TEAM='CX EMEA'
export CWT_MANAGER='First Last'
export CWT_JOB='Customer Delivery Architect'
export CWT_DELIVERABLE='Design Document'
```

Then source it before running the script:

```bash
source .env
```

**Security note:** The `.gitignore` already excludes `.env*` files. Never commit cookies or CSRF tokens to version control.

### 3.5 Run a Dry-Run Submission

Before submitting for real, test the request with `--dry-run`:

```bash
python3 scripts/submit_creative_work.py \
    --dry-run \
    --title "NSO Service Pack v2 design doc" \
    --url "https://wwwin-github.cisco.com/mmalysz/nso-svc/blob/main/docs/v2.md" \
    --org "CX" \
    --team "CX EMEA" \
    --manager "First Last" \
    --job "Customer Delivery Architect" \
    --deliverable "Design Document"
```

**Expected output:**

```
DRY RUN — would POST to: https://cxpp-external-proxy-alln.cisco.com/creative-work-tool/creative-work-add
  _csrf: fa38c8ee…
  creativeWorkTitle: NSO Service Pack v2 design doc
  reporterName: Maciej Małysz
  organizationName: CX
  teamName: CX EMEA
  managerName: First Last
  jobTitle: Customer Delivery Architect
  deliverableName: Design Document
  url: https://wwwin-github.cisco.com/mmalysz/nso-svc/blob/main/docs/v2.md
```

If the output looks correct, proceed to the real submission.

### 3.6 Submit for Real

Remove `--dry-run` and run again:

```bash
python3 scripts/submit_creative_work.py \
    --title "NSO Service Pack v2 design doc" \
    --url "https://wwwin-github.cisco.com/mmalysz/nso-svc/blob/main/docs/v2.md" \
    --org "CX" \
    --team "CX EMEA" \
    --manager "First Last" \
    --job "Customer Delivery Architect" \
    --deliverable "Design Document"
```

**Expected output:**

```
OK (302) — redirected to https://cxpp-external-proxy-alln.cisco.com/creative-work-tool/
```

An HTTP 302 redirect back to the dashboard means **success**.

### 3.7 Verify the Submission

1. Refresh `https://cxpp-external-proxy-alln.cisco.com/creative-work-tool/` in your browser.
2. You should see a new row in the current month's table with:
   - **Title**: `NSO Service Pack v2 design doc`
   - **Status**: `Pending` (yellow badge)
   - **Deliverable**: `Design Document`
3. The status will change to `Approved` (green) or `Declined` (red) after your manager reviews it.

---

## 4. Path B — GitHub PR-Based Submission

Use this path when your creative work is delivered as **merged GitHub pull requests**. The Creative Work Tool has a built-in GitHub integration that fetches closed/merged PRs since the **26th of the previous month** (matching the Polish payroll cutoff).

### 4.1 How the GitHub PR Import Works

1. You configure a **GitHub Personal Access Token (PAT)** or complete the **GitHub OAuth flow** in the tool's profile settings.
2. The tool stores your GitHub credentials server-side.
3. When you click **Import from GitHub** on the dashboard, the tool queries GitHub for all **closed/merged** PRs where you are the **author**, closed since the **26th of the previous month**.
4. You tick the PRs that count as creative work, accept the statutory statement, and click **Save**.
5. The tool creates one entry per selected PR with `deliverableName=Code Contribution` (or whatever you set in the form).

**Date window:** The tool hard-codes the query to `closed:>=YYYY-MM-26` where `YYYY-MM` is the previous calendar month. For example, if today is 2026-04-22, the tool fetches PRs closed since 2026-03-26.

**Supported hosts:**
- `github.com` (public GitHub)
- `wwwin-github.cisco.com` (Cisco internal GitHub Enterprise)

The tool may support only one host per credential. Check the tool's profile page to see which host your PAT or OAuth connection is configured for.

### 4.2 GitHub Authentication Options

You have two options for authenticating with GitHub:

#### Option A: Fine-Grained Personal Access Token (Recommended)

1. Go to `https://github.com/settings/tokens?type=beta` (for github.com) or `https://wwwin-github.cisco.com/settings/tokens?type=beta` (for Cisco GHE).
2. Click **Generate new token** → **Fine-grained personal access token**.
3. Set:
   - **Token name**: `Creative Work Tool`
   - **Expiration**: 90 days (or longer)
   - **Repository access**: Select the repositories you want to include (or "All repositories" if you trust the tool)
   - **Permissions**: `Pull requests: Read-only`
4. Click **Generate token** and copy the token (starts with `github_pat_…`).
5. In the Creative Work Tool, go to **Profile** → **GitHub** → paste the token → **Save**.

#### Option B: GitHub OAuth (In-Tool Flow)

1. In the Creative Work Tool, go to **Profile** → **GitHub** → **Connect via OAuth**.
2. You will be redirected to GitHub's OAuth authorization page.
3. Review the requested permissions (read access to your PRs) and click **Authorize**.
4. You will be redirected back to the tool with a success message.

**Security note:** The tool stores your GitHub credentials server-side. If you are uncomfortable with this, use a fine-grained PAT scoped to only the repositories you want to include, and set a short expiration (e.g. 30 days).

### 4.3 Pre-Flight: What PRs Will the Tool See?

Before opening the tool, you can preview what PRs the tool will offer to import using the `list_github_prs.py` script.

**For github.com:**

```bash
export GH_TOKEN="github_pat_11AAAAAA…"  # your fine-grained PAT
python3 scripts/list_github_prs.py --since-26th
```

**For Cisco internal GitHub:**

```bash
export GH_TOKEN="github_pat_11AAAAAA…"  # your Cisco GHE PAT
python3 scripts/list_github_prs.py --host wwwin-github.cisco.com --since-26th
```

**Expected output:**

```
5 closed PR(s) since 2026-03-26 on github.com:

CLOSED      REPO                                     #      TITLE
----------------------------------------------------------------------------------------------------
2026-04-15  maciejmalysz/creative                    #2     [creative] Add usage guide for both submission paths
2026-04-10  maciejmalysz/nso-svc                     #12    Fix NSO service template validation
2026-03-28  maciejmalysz/radkit-proxy                #8     Add RADKit certificate auth support
2026-03-27  maciejmalysz/opencode-config             #45    Update MCP server configuration skill

These are the PRs the Creative Work Tool will offer in 'Import from GitHub'.
Tip: prefix titles with [creative] to make them easy to spot in the picker.
```

**What this tells you:**
- The tool will show 4 PRs (all closed since 2026-03-26).
- The first PR has a `[creative]` prefix — this makes it easy to spot in the tool's picker.
- The other PRs do not have the prefix — you can still select them, but they may be harder to identify if you have many PRs.

**Tip:** Prefix your PR titles with `[creative]` to make them easy to spot in the tool's picker. For example:
- `[creative] Design Document: NSO Service Pack v2`
- `[creative] Code Contribution: RADKit certificate auth`

### 4.4 Mark PRs for Import (Optional)

If you want to mark PRs in advance so you remember which ones to select in the tool, you can:

1. **Add a label** to the PR (e.g. `creative-work`) — this requires write access to the repository.
2. **Prefix the PR title** with `[creative]` — this is visible in the tool's picker and does not require any special permissions.

**Example PR title:**

```
[creative] Design Document: NSO Service Pack v2 architecture
```

**Note:** The tool does **not** filter by label or title prefix — it shows **all** closed/merged PRs since the 26th. The prefix is purely for your own convenience when selecting PRs in the tool.

### 4.5 Import PRs via the Tool

1. Open `https://cxpp-external-proxy-alln.cisco.com/creative-work-tool/` in your browser.
2. Complete the Duo SSO challenge if prompted.
3. On the dashboard, click **Import from GitHub**.
4. The tool fetches all closed/merged PRs since the 26th of the previous month.
5. You will see a list of PRs with checkboxes. Each PR shows:
   - Repository name
   - PR number and title
   - Closed date
6. **Tick the PRs** that count as creative work.
7. **Accept the statutory statement** (checkbox at the bottom).
8. Click **Save**.
9. The tool creates one entry per selected PR with status `Pending`.

**Expected lifecycle:**
- **Pending** (yellow) — waiting for manager approval.
- **Approved** (green) — manager approved, will be included in next payroll.
- **Declined** (red) — manager declined, will not be included.

### 4.6 Verify the Import

1. Refresh the dashboard.
2. You should see new rows in the current month's table, one per selected PR.
3. Each row shows:
   - **Title**: PR title (e.g. `[creative] Add usage guide for both submission paths`)
   - **Status**: `Pending`
   - **Deliverable**: `Code Contribution` (or whatever you set in the form)
   - **URL**: Link to the PR on GitHub

---

## 5. Skill Usage

If you use OpenCode or Claude Code with the `creative-work-submit` skill, you can invoke it by saying:

- "Submit creative work"
- "Report creative work"
- "Creative work tool"
- "Copyright submission"
- "Submit to the creative work tool"

The skill will ask you which path you want to use (Path A or Path B) and guide you through the steps.

**Example prompts:**

```
"Submit my NSO design doc to the creative work tool"
→ Skill invokes Path A, asks for title/URL/metadata, runs dry-run, then real submission.

"Import my GitHub PRs from the past month"
→ Skill invokes Path B, runs list_github_prs.py, shows preview, guides you to the tool.

"Submit creative work for both my design doc and my GitHub PRs"
→ Skill runs Path B first (imports PRs), then Path A for the design doc.
```

**Skill location:** `skills/creative-work-submit/SKILL.md` in this repository.

---

## 6. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| **HTTP 302 redirect to `sso.duosecurity.com`** | Duo session expired | Open the tool in your browser, complete Duo SSO, re-capture `CWT_COOKIE` and `CWT_CSRF` (see section 3.2) |
| **HTTP 403 with "Invalid CSRF token"** | CSRF token rotated (happens on every page load) | Refresh the dashboard in your browser, re-capture the `_csrf` value from DevTools, re-export `CWT_CSRF` |
| **Submission succeeds (HTTP 302) but no row appears in dashboard** | Server validation rejected an unknown dropdown value | Re-capture the live dropdown options (see section 3.3) and confirm `--org`, `--team`, `--manager`, `--job`, `--deliverable` exactly match the tool's expected values |
| **`list_github_prs.py` returns empty list** | (a) PAT lacks repo access, or (b) you are not the PR author | (a) Switch to a fine-grained PAT scoped to the right repositories with "Pull requests: Read", or (b) verify with `gh pr list --author @me --state merged --search "closed:>=YYYY-MM-26"` |
| **Tool's "Import from GitHub" shows fewer PRs than `list_github_prs.py`** | Tool may use stricter scope (only repos the PAT explicitly grants) or only one host (github.com vs Cisco GHE) | Check the tool's profile page for which credential is connected and what host it talks to. If using a fine-grained PAT, ensure it has access to all repositories you want to include. |
| **HTTP 401 from GitHub API** | PAT is invalid or expired | Generate a new PAT (see section 4.2) and update the tool's profile or re-export `GH_TOKEN` |
| **Tool shows "No PRs found"** | (a) No closed/merged PRs since the 26th, or (b) GitHub credential not configured | (a) Verify with `list_github_prs.py --since-26th`, or (b) go to Profile → GitHub and configure a PAT or OAuth connection |
| **User asks to "submit on behalf of someone else"** | Not supported — each user must use their own Duo session | Refuse — each user must run with their own Duo session and own cookie. There is no admin path, and impersonating another payroll claim is a policy violation. |

**Additional help:**
- **Tool support**: `itdcsupport@cisco.com`
- **Procedure questions**: HelpZone → Pay Inquiry → "creative work"
- **KB article**: https://cisco.service-now.com/helpzone?id=kb_article&sysparm_article=KB0066779

---

## 7. Security Notes

### 7.1 Never Commit Secrets

The following must **never** be committed to version control:
- Session cookies (`CWT_COOKIE`)
- CSRF tokens (`CWT_CSRF`)
- GitHub Personal Access Tokens (`GH_TOKEN`)
- Any `.env` files containing the above

The `.gitignore` in this repository already excludes `.env*` files. If you accidentally commit a secret, **immediately revoke it** (for PATs: go to GitHub settings and delete the token; for cookies: log out of the tool and re-authenticate).

### 7.2 Use Environment Variables or Keychain

**Recommended storage:**
- **Environment variables** (for short-lived secrets like cookies/CSRF): `export CWT_COOKIE='…'` in your shell session.
- **macOS Keychain** (for long-lived secrets like PATs): `security add-generic-password -s "creative-work-tool-gh-token" -a "$USER" -w "github_pat_…"`

**Avoid:**
- Hardcoding secrets in scripts or config files.
- Storing secrets in plain text files in your home directory (unless the file is `chmod 600` and you trust your backup system).

### 7.3 Scope GitHub PATs Narrowly

When creating a fine-grained PAT for Path B:
- **Repository access**: Select only the repositories you want to include (or "All repositories" if you trust the tool).
- **Permissions**: `Pull requests: Read-only` is sufficient. Do **not** grant write access.
- **Expiration**: Set a short expiration (e.g. 30–90 days) and renew as needed.

### 7.4 Audit Your Submissions

The Creative Work Tool dashboard shows all your submissions for the current month. Review it periodically to ensure:
- No duplicate entries (the tool de-duplicates server-side, but it's good to check).
- No incorrect entries (if you accidentally submitted the wrong PR, contact your manager to decline it).
- All expected entries are present (if a submission failed silently, you may need to re-submit).

---

## 8. Appendix: Sample `.env` Template

Save this to `.env` in the project root (already excluded by `.gitignore`):

```bash
# .env — Creative Work Tool credentials
# DO NOT COMMIT THIS FILE

# Path A — Manual submission
export CWT_COOKIE='SESSION=abc123def456; ITDC_AUTH=xyz789'
export CWT_CSRF='fa38c8ee-f474-44cc-88fa-09298a459867'

# Path A — Default metadata (optional, saves typing)
export CWT_ORG='CX'
export CWT_TEAM='CX EMEA'
export CWT_MANAGER='First Last'
export CWT_JOB='Customer Delivery Architect'
export CWT_DELIVERABLE='Design Document'

# Path B — GitHub pre-flight
export GH_TOKEN='github_pat_11AAAAAA…'

# Usage:
#   source .env
#   python3 scripts/submit_creative_work.py --title "…" --url "…" --org "$CWT_ORG" --team "$CWT_TEAM" --manager "$CWT_MANAGER" --job "$CWT_JOB" --deliverable "$CWT_DELIVERABLE"
```

**Security reminder:** This file is excluded by `.gitignore`. Never commit it. If you share this repository, ensure `.env` is not included in the archive.

---

## 9. Appendix: Quick Reference

### Path A — Manual Submission

```bash
# 1. Capture cookie + CSRF (one-time per Duo session)
python3 scripts/submit_creative_work.py --capture-help

# 2. Export credentials
export CWT_COOKIE='SESSION=…; ITDC_AUTH=…'
export CWT_CSRF='fa38c8ee-…'

# 3. Dry-run
python3 scripts/submit_creative_work.py \
    --dry-run \
    --title "My Design Doc" \
    --url "https://wwwin-github.cisco.com/user/repo/blob/main/docs/design.md" \
    --org "CX" --team "CX EMEA" \
    --manager "First Last" --job "Customer Delivery Architect" \
    --deliverable "Design Document"

# 4. Real submission (remove --dry-run)
python3 scripts/submit_creative_work.py \
    --title "My Design Doc" \
    --url "https://wwwin-github.cisco.com/user/repo/blob/main/docs/design.md" \
    --org "CX" --team "CX EMEA" \
    --manager "First Last" --job "Customer Delivery Architect" \
    --deliverable "Design Document"
```

### Path B — GitHub PR Import

```bash
# 1. Pre-flight (what will the tool see?)
export GH_TOKEN='github_pat_…'
python3 scripts/list_github_prs.py --since-26th

# 2. Open the tool, click "Import from GitHub", tick PRs, Save
open https://cxpp-external-proxy-alln.cisco.com/creative-work-tool/
```

---

**End of Usage Guide**
