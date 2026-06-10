# NEXT RUN — Resume Procedure

**Purpose:** Anything Maciej or a future AI session needs to update the rolling-30-day creative-work suggestion and submit it.

**Last run:** 2026-06-10 (window: 2026-05-11 → 2026-06-10) → 13 candidates.

**Target next run:** ~2026-06-17 (one week later).

---

## TL;DR for the AI session

Maciej will say something like:
- "update the creative work suggestion"
- "regenerate the last-30-days creative report"
- "let's do this week's creative submission"

When that happens, do **all** of the following without asking for clarification:

1. **Compute the rolling window** = `[today - 30 days, today]`. Use the actual current date.
2. **Pull the merged-PR list** from Cisco GHE (active account = `mmalysz` on `wwwin-github.cisco.com`):
   ```bash
   GH_HOST=wwwin-github.cisco.com gh search prs \
       --author=@me --merged \
       --closed=">=YYYY-MM-DD" \
       --limit 100 \
       --json repository,title,number,closedAt,url
   ```
   Also check `github.com` (active account = `mmalysz_cisco`, but switch to `maciejmalysz` for personal repos):
   ```bash
   gh search prs --author=@me --merged --closed=">=YYYY-MM-DD" --limit 100 \
       --json repository,title,number,closedAt,url
   ```
3. **Scan local repo activity** for non-PR authorship (docs, configs, skills) since the window start:
   ```bash
   for d in ~/Projects/opencode-config ~/Projects/du-fwa-support ~/Projects/creative; do
     echo "=== $d ==="
     git -C "$d" log --author="mmalysz\|Maciej" --since="YYYY-MM-DD" \
         --pretty="%h %ad %s" --date=short
   done
   ```
4. **Triage into tiers** using the rules below, then **generate two artifacts** in `~/Projects/creative/`:
   - `creative-work-YYYY-MM-DD_to_YYYY-MM-DD.md` (markdown source list)
   - `docs/suggestion-YYYY-MM-DD_to_YYYY-MM-DD.html` (Cisco-branded HTML report)
5. **Commit and push** to both remotes (`cisco` and `origin`). Use the same Co-authored-by trailer.
6. **Verify Pages** is serving the new HTML (HTTP 200) and give Maciej the link:
   `https://wwwin-github.cisco.com/pages/mmalysz/creative/suggestion-YYYY-MM-DD_to_YYYY-MM-DD.html`
7. **If Maciej says "submit"**, follow the **Submission** section below (NOT before — he reviews first).

---

## Triage rules

| Tier | What goes here |
|------|----------------|
| **Tier 1** | Merged PRs in Cisco GHE with substantive original code/design (algorithms, YANG models, workflows, devcontainers, novel fixes). One bullet per PR. Group related PRs (e.g. Kafka 2 MB rollout #705 + #706) under one item. |
| **Tier 2** | Documentation authorship, skill/agent specs, multi-commit configuration work in tracked repos *without* a single merging PR. Use commit hashes as evidence. |
| **Tier 3** | Minor but original work — small fixes, curation passes, single-commit refactors. |
| **Excluded** | Routine ops/case-management commits, PII-scrub mechanical renames, CI hotfixes that are pure boilerplate, anything outside the date window. List exclusions explicitly under "Excluded for traceability". |

---

## Source paths (last verified 2026-06-10)

- **Active GH accounts** (verify with `gh auth status`):
  - `github.com` → active = `mmalysz_cisco` (work scopes), secondary = `maciejmalysz` (personal mirror push)
  - `wwwin-github.cisco.com` → `mmalysz`
- **Repo:** `~/Projects/creative` — origin = `github.com/maciejmalysz/creative` (tracked branch), cisco = `wwwin-github.cisco.com/mmalysz/creative` (Pages source)
- **Pages branch/path:** `main` / `/docs` (legacy build, public within Cisco)
- **Pages base URL:** `https://wwwin-github.cisco.com/pages/mmalysz/creative/`
- **Project orgs to expect PRs from:** `TKSB-POWER`, `mmalysz`, `AS-DU-NSO`, `DU-DEV-TEAM` (PAT must have `Pull requests: Read` on these for the tool's Path B import)

---

## HTML template

Use the **existing report** as the template — copy `docs/suggestion-2026-05-11_to_2026-06-10.html`, change:
- `<title>` and hero dates
- `Generated` meta-card date
- Summary stat counts
- Tier sections (replace items, keep card structure)
- Footer date

Styling, navbar, "← Project home" link, and `cisco.css` reference must remain unchanged.

---

## Push procedure (verbatim)

```bash
cd ~/Projects/creative
git add -A
git -c user.email=mmalysz@cisco.com commit -m "docs: update creative-work suggestion (YYYY-MM-DD → YYYY-MM-DD)

<one-line summary>

Co-authored-by: Claude Opus 4.7 Github Copilot <noreply@github.com>"

# Push to cisco (primary, drives Pages)
git push cisco main

# Push to origin (personal mirror) — needs account switch
gh auth switch -h github.com -u maciejmalysz
git push origin main
gh auth switch -h github.com -u mmalysz_cisco
```

**Verify Pages:** wait ~8s after push, then:
```bash
curl -sI -o /dev/null -w "%{http_code}\n" \
  "https://wwwin-github.cisco.com/pages/mmalysz/creative/suggestion-YYYY-MM-DD_to_YYYY-MM-DD.html"
```
Expect `200`.

---

## Submission (only when Maciej confirms)

Path B (recommended for merged PRs) and Path A (for docs/local work) are documented in the `creative-work-submit` skill (`~/.config/opencode/skills/creative-work-submit/SKILL.md`). Load it. Steps:

1. Pre-flight what the tool will see:
   ```bash
   export GH_TOKEN="<Cisco GHE fine-grained PAT, Pull requests: Read>"
   python3 ~/Projects/creative/scripts/list_github_prs.py \
       --host wwwin-github.cisco.com --since YYYY-MM-DD
   ```
2. Verify Duo SSO session at `https://cxpp-external-proxy-alln.cisco.com/creative-work-tool/`. If `CWT_COOKIE` / `CWT_CSRF` env vars are stale, re-capture per skill instructions.
3. Path B — use the tool's **Import from GitHub** UI for Tier 1 + #11.
4. Path A — for each non-PR Tier 2/3 item, run:
   ```bash
   python3 ~/Projects/creative/scripts/submit_creative_work.py \
       --dry-run \
       --title "<title>" --url "<link>" \
       --org "..." --team "..." --manager "..." --job "..." --deliverable "..."
   ```
   Drop `--dry-run` to actually submit. `302` to dashboard = success.
5. Refresh dashboard, confirm new rows show status `Pending`.

---

## Known gotchas

- **`origin` push fails with 403** → wrong active GH account. Switch to `maciejmalysz` first, then push, then switch back to `mmalysz_cisco`.
- **`origin` push fails non-fast-forward** → origin has merge commits from PRs not pulled locally. Run `git pull --rebase origin main`, then push to origin (fast-forward), then `git push cisco main --force-with-lease` to align cisco.
- **`gh search prs` rejects `mergedAt`** → use `closedAt` with `state:merged` (auto-applied by `--merged`).
- **"Updates were rejected"** to cisco after rebase → use `--force-with-lease` (never plain `--force`).
- **Co-authored-by trailer** is mandatory on every commit (per `~/.config/opencode/AGENTS.md`).

---

## Files to read on resume

When Maciej comes back, read in this order:
1. This file (`NEXT_RUN.md`) — procedure
2. `creative-work-2026-05-11_to_2026-06-10.md` — last source list (format reference)
3. `docs/suggestion-2026-05-11_to_2026-06-10.html` — last HTML report (template)
4. `~/.config/opencode/skills/creative-work-submit/SKILL.md` — submission paths (only when submitting)
