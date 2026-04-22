# Design — Creative Work Submission Automation

**Owner**: Maciej Małysz (mmalysz@cisco.com)
**Last updated**: 2026-04-22
**Target system**: `https://cxpp-external-proxy-alln.cisco.com/creative-work-tool/` (v1.0.23-SNAPSHOT)
**Reference**: KB0066779 — Employee creative work and copyrights salary – Poland

---

## 1. Goal

Reduce the click-cost of submitting eligible creative work each month by
automating the two flows the Creative Work Tool already exposes:

1. **Path A** — direct submission of a single piece of creative work
   (title + deliverable type + link).
2. **Path B** — bulk import of merged GitHub pull requests (the tool's most
   complete native feature).

Both paths must work for **github.com** and **wwwin-github.cisco.com** sources
because the eligible work spans both.

## 2. Non-goals

- Replacing the Creative Work Tool's UI for manager approvals.
- Submitting on behalf of *other* employees (each user must run with their own
  Duo session).
- Bypassing Duo SSO (we ride an existing browser session — no credential
  handling).

## 3. System inventory (what the tool actually exposes)

Captured live on 2026-04-22 by a CDP-driven Chrome under the user's authenticated
Duo session. Full schema in [`api-reference.md`](api-reference.md).

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/creative-work-tool/user-info-update` | POST | Update reporter profile (org, team, manager, job, deliverable) |
| `/creative-work-tool/creative-work-add` | POST (multipart) | **Path A** — submit one piece of creative work |
| `/creative-work-tool/creative-work-github-add` | POST | **Path B** — submit selected PRs in bulk |
| `/creative-work-tool/status-update` | POST | Manager approve/decline (out of scope) |
| `/creative-work-tool/github/authorize` | redirect | Start GitHub OAuth flow inside the tool |
| `/creative-work-tool/github/disconnect` | POST | Drop stored GitHub credentials |

All POSTs require:
- A valid **Duo SSO session cookie** on `cxpp-external-proxy-alln.cisco.com`.
- A **CSRF token** (`_csrf`) issued per page load and embedded as a hidden field
  in every form.

## 4. Path A — manual submission

**Form**: `#reportCreativeWorkForm`, multipart, fields:

| Field | Type | Source / notes |
|-------|------|----------------|
| `creativeWorkTitle` | text, required | Free text |
| `reporterName` | text, required | Pre-filled from profile |
| `organizationName` | select, required | Closed list (CX, Engineering …, Sales, Splunk …, etc.) |
| `teamName` | select, required | Depends on org |
| `managerName` | select, required | Depends on team |
| `jobTitle` | select, required | Depends on team |
| `deliverableName` | select, required | Depends on team (e.g. *Design Document*, *Code Contribution*) |
| `url` | url, required | Link to the work |
| `deliverableFileUpload` | file, optional | Synced to SharePoint `ITDCSubmissions/Submissions/<short-id>` |
| `_csrf` | hidden, required | From the page |

**Implementation**: `scripts/submit_creative_work.py` — pure-stdlib (urllib +
http.cookiejar). User exports `CWT_COOKIE` and `CWT_CSRF` once per browser
session; the script POSTs and prints the new entry's status.

## 5. Path B — GitHub PR import

The tool already implements this end-to-end:

1. User stores a **fine-grained GitHub PAT** (`type=beta`) in their profile, or
   completes the in-tool **GitHub OAuth** flow.
2. On dashboard load, the **server** calls GitHub on behalf of the user and
   collects all **closed/merged** PRs authored by the user, **since the 26th of
   the previous month** (matches the payroll cutoff).
3. User ticks the PRs that count, accepts the statement, **Save** →
   `POST /creative-work-github-add`.

We do not need to re-implement any of that. What we *do* add:

- **`scripts/list_github_prs.py`** — local pre-flight that mirrors the tool's
  query (`is:pr is:closed author:@me closed:>=YYYY-MM-26`) so the user can see
  what *will* show up before opening the tool.
- **`.github/workflows/creative-work-tag.yml`** — auto-labels merged PRs in
  *this* repo with `creative-work` so the user has a consistent grep target
  later (in the tool, the PR title is what shows; consistent prefixes help).
- **`.github/pull_request_template.md`** — encourages PR titles like
  `[creative] <deliverable type>: <title>` so they read well in the tool.

## 6. Decision: skill + scripts vs MCP server

| Criterion | Skill + scripts (chosen) | MCP server |
|-----------|--------------------------|------------|
| Auth | Reuses user's Duo browser session via cookie+CSRF capture | Same — no real win |
| Coverage of Path B | None needed (tool does it server-side) | Same |
| Maintenance | 2 small Python files, no daemon | Long-running server, OAuth refresh, restart loops |
| Sharing across users | One-off paste of cookie/csrf | Could be a value-add **only if** ≥3 colleagues want it |
| Time to first submission | Minutes | Days |
| Failure blast radius | Single user, single submission | Service-wide |

**Decision**: Ship the skill + scripts. Revisit MCP if/when other Polish CX
engineers ask to share a refresh service.

## 7. Threat model & guardrails

| Threat | Mitigation |
|--------|------------|
| Cookie/CSRF leakage to logs or git | Read from env vars only; `.gitignore` excludes any `.env*`; script never echoes the cookie |
| Submitting on behalf of someone else | Each run uses *that user's* browser session; impossible without their Duo approval |
| Wrong PR imported and counted twice | Tool already de-duplicates server-side; pre-flight script flags PRs already imported (TODO once `/creative-work-list` JSON is reverse-engineered) |
| PAT scope creep | Recommend fine-grained PAT, read-only, repo-scoped — documented in skill |

## 8. Open questions

- **Pre-flight de-dupe**: We can't yet read previously imported entries
  programmatically (the dashboard renders HTML; no JSON list endpoint observed).
  Workaround: the tool itself blocks duplicates server-side. Revisit if we hit
  this in practice.
- **Attachment upload for Path A**: `deliverableFileUpload` is multipart and
  goes to SharePoint. v1 supports URL-only; file upload tracked as
  `TODO(scripts/submit_creative_work.py:upload-file)`.

## 9. Future work

- MCP server (`creative-work-mcp`) exposing `submit`, `list_my_prs`,
  `import_prs` tools — only if shared use materialises.
- Calendar reminder: 25th of each month auto-runs `list_github_prs.py
  --since-26th` and emails the user.
- `wwwin-github.cisco.com` PR coverage — verify tool's GitHub client supports
  GHE; if not, add a thin POST adapter.
