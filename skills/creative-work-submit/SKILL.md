---
name: creative-work-submit
description: Submit creative work to the Cisco Creative Work Tool (Polish copyright procedure, KB0066779). Two paths — manual POST or GitHub PR import. Use when the user says 'submit creative work', 'creative work tool', 'copyright submission', 'report creative work', or refers to the monthly creative work submission. Requires Duo SSO session on cxpp-external-proxy-alln.cisco.com.
---

# Skill: creative-work-submit

## Tier 0

- **What**: Drives the Cisco Creative Work Tool (`https://cxpp-external-proxy-alln.cisco.com/creative-work-tool/`) for the Polish creative work / copyright payroll procedure.
- **When**: User wants to submit, list, or pre-flight creative work entries — either standalone deliverables or merged GitHub PRs.
- **Inputs**: Title + link (Path A) **or** GitHub PAT for PR list (Path B). Always: an active Duo SSO session for the proxy host.
- **Output**: New row(s) in the user's Creative Work Tool dashboard with status `Pending`.

## Tier 1

### Path decision

Ask the user once, then proceed:

- **"Are you submitting one specific piece of work, or importing GitHub PRs from the past month?"**
  - **One piece** → Path A.
  - **GitHub PRs** → Path B.
  - **Both** → run Path B first (covers most engineering work), then Path A for non-PR items (docs, presentations, recordings).

### Path A — manual submission

1. Confirm the user has env vars set:
   ```bash
   echo "${CWT_COOKIE:+set}" "${CWT_CSRF:+set}"
   ```
   If either is empty, run:
   ```bash
   python3 ~/Projects/creative/scripts/submit_creative_work.py --capture-help
   ```
   and walk the user through capturing them from their authenticated browser. **Never** ask the user to paste the cookie into chat — they export it locally.
2. Verify dropdown values for org/team/manager/job/deliverable. If unsure, ask the user to read them off the open Report modal in their browser, or use the JS snippet in `docs/api-reference.md` to dump them once.
3. Run a dry-run first:
   ```bash
   python3 ~/Projects/creative/scripts/submit_creative_work.py \
       --dry-run \
       --title "<title>" --url "<link>" \
       --org "<org>" --team "<team>" \
       --manager "<manager>" --job "<job>" --deliverable "<deliverable>"
   ```
4. Drop `--dry-run` to actually submit. A `302` to the dashboard means success.
5. Tell the user to confirm the new row appears in the tool with status `Pending`.

### Path B — GitHub PR import

1. Pre-flight what the tool will see:
   ```bash
   export GH_TOKEN="github_pat_…"   # ask user to set this once
   python3 ~/Projects/creative/scripts/list_github_prs.py --since-26th
   # for Cisco internal:
   python3 ~/Projects/creative/scripts/list_github_prs.py --host wwwin-github.cisco.com --since-26th
   ```
2. If the list looks right:
   - Open the tool, click **Import from GitHub**.
   - Tick the relevant PRs, accept the statement, **Save**.
3. If the list is empty or wrong:
   - Verify the PAT has read access to the right repos (fine-grained, repo-scoped, "Pull requests: Read").
   - Check the user is the PR **author** (the tool filters on `author:@me`).

### Verifying the submission

Refresh `https://cxpp-external-proxy-alln.cisco.com/creative-work-tool/` — new entries appear in the current month's table with status `Pending` until manager approves.

## Tier 2

- [ ] Project repo: `https://github.com/maciejmalysz/creative`
- [ ] Design doc: `~/Projects/creative/docs/DESIGN.md`
- [ ] API reference: `~/Projects/creative/docs/api-reference.md`
- [ ] Path A script: `~/Projects/creative/scripts/submit_creative_work.py`
- [ ] Path B pre-flight: `~/Projects/creative/scripts/list_github_prs.py`
- [ ] KB article: https://cisco.service-now.com/helpzone?id=kb_article&sysparm_article=KB0066779
- [ ] Tool support: `itdcsupport@cisco.com`
- [ ] Related skill: `cdp-browser-automation` (use to capture cookie/CSRF or to drive the tool UI when scripts are blocked)

## Common failure modes

1) **Symptom:** Script returns HTTP 302 to a `sso.duosecurity.com` URL.
   **Smallest fix:** Duo session expired. Open the tool in Chrome, re-auth, re-export `CWT_COOKIE` and `CWT_CSRF`. Sessions usually last 8–10 hours.

2) **Symptom:** HTTP 403 with `Invalid CSRF token`.
   **Smallest fix:** The CSRF rotates per page load — refresh the dashboard in the browser, copy the new `_csrf`, re-export `CWT_CSRF`.

3) **Symptom:** Submission succeeds (302) but no row appears in the dashboard.
   **Smallest fix:** Server validation may have silently rejected an unknown dropdown value. Re-capture the live dropdown options (see `docs/api-reference.md` JS snippet) and confirm `--org/--team/--manager/--job/--deliverable` exactly match.

4) **Symptom:** GitHub PR list (`list_github_prs.py`) is empty but you know you have merged PRs.
   **Smallest fix:** Either (a) the PAT lacks repo access — switch to a fine-grained PAT scoped to the right org with "Pull requests: Read", or (b) you weren't the author (PRs you merged for someone else don't count) — verify with `gh pr list --author @me --state merged`.

5) **Symptom:** Tool's "Import from GitHub" shows fewer PRs than `list_github_prs.py`.
   **Smallest fix:** The tool may use a stricter scope (only repos the PAT explicitly grants) or only one host (github.com vs Cisco GHE). Check the tool's profile page for which credential is connected and what host it talks to.

6) **Symptom:** User asks to "submit on behalf of someone else".
   **Smallest fix:** Refuse — each user must run with their own Duo session and own cookie. There is no admin path here, and impersonating another payroll claim is a policy violation.
