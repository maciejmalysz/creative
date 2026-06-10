# Creative Work — May 2026

**Author:** Maciej Malysz (mmalysz@cisco.com)
**Period:** 2026-05-01 → 2026-05-31 (in progress; generated 2026-05-20)
**Purpose:** Source list for submission to Cisco Creative Work Tool (KB0066779, Polish copyright procedure)

---

## Tier 1 — Strongest Candidates

### 1. DU_FWA_Day2_System — Monorepo Consolidation & Registry Migration

- **Type:** Internal tooling / automation refactor
- **Description:** Consolidated multiple Day2 SPIS automation repos into a single monorepo and migrated container registry references from `xiawang3` to the team-owned `du-fwa-auto-repo`. Restructured build/deploy pipelines and updated all downstream references.
- **Location:** `~/Projects/DU_FWA_Day2_System/` — commits `c111b5f`, `b81181d`, `1878528`
- **Why qualifies:** Substantial architectural refactor; original design decisions on module boundaries, registry topology, and deploy flow.

### 2. DU_FWA_Day2_System — Webex Auto-Add from Active Engineer DB

- **Type:** Code / automation
- **Description:** Replaced the static `WEBEX_MAILER` recipient list with a dynamic lookup against the active-engineer database. Webex space membership now self-maintains as the on-call roster changes.
- **Location:** `~/Projects/DU_FWA_Day2_System/` — commit `5326b85`
- **Why qualifies:** Novel integration logic between engineer DB and Webex API; eliminates manual roster maintenance.

### 3. DU_FWA_Day2_System — OAuth State Relax + Jira ADF 400 Fix

- **Type:** Code / bug fix with original design
- **Description:** Relaxed OAuth state validation to tolerate provider-side query-string mutations, and fixed Jira ADF (Atlassian Document Format) requests that returned HTTP 400 due to empty paragraph nodes by filtering them before submission.
- **Location:** `~/Projects/DU_FWA_Day2_System/` — commit `d6005f5`
- **Why qualifies:** Required reverse-engineering Jira's ADF schema and OAuth flow edge cases; original mitigation.

### 4. du-fwa-support — Initial Publication (RCAs / Ops KB)

- **Type:** Documentation / knowledge base
- **Description:** First public commit of the DU FWA support knowledge base: root-cause analyses, operational runbooks, and structured case-handling guidance for the Day2 SPIS firewall automation platform.
- **Location:** `~/Projects/du-fwa-support/` — commit `4986c2f`
- **Why qualifies:** Original written work; structured KB design from scratch.

### 5. Day2 SPIS — User Onboarding Procedure

- **Type:** Documentation / procedure
- **Description:** End-to-end onboarding procedure for new Day2 SPIS users, including the `set_state_here` OAuth warning workaround and step-by-step environment setup.
- **Location:** `~/Projects/du-fwa-support/` — commits `9e3aab4`, `c5214ac`
- **Why qualifies:** Original procedural documentation derived from troubleshooting experience.

---

## Tier 2 — Supporting Candidates

### 6. Day2 SPIS — B3–B10 Config Issues Documentation

- **Type:** Documentation / troubleshooting guide
- **Description:** Cataloged configuration issues across SPIS bundles B3 through B10 with diagnostic steps and fixes.
- **Location:** `~/Projects/du-fwa-support/` — commit `ceecedf`
- **Why qualifies:** Original diagnostic synthesis across multiple deployment bundles.

### 7. Apply-Patches Rollout Guide — B1 / B3–B10

- **Type:** Documentation / runbook
- **Description:** Operational rollout guide for the apply-patches workflow covering bundles B1 and B3–B10, including sequencing, rollback, and verification steps.
- **Location:** `~/Projects/du-fwa-support/` — commit `98a6cb9`
- **Why qualifies:** Original operational procedure design.

### 8. Day2 Build-Deploy Credentials Map + Live-Migration Runbook

- **Type:** Documentation / runbook
- **Description:** Authored a credentials-flow map for the Day2 build-deploy pipeline and a live-migration runbook for zero-downtime transitions.
- **Location:** `~/Projects/du-fwa-support/` — commits `a18a1cc`, `35cc5aa`
- **Why qualifies:** Original architectural documentation and migration design.

### 9. ~/Projects/AGENTS.md — Auto-Boot + MCP Specification

- **Type:** Agent / skill specification (technical writing)
- **Description:** Specification governing per-session auto-boot behavior for AI agents working in `~/Projects/`, including MCP server expectations and project-discovery rules.
- **Location:** `~/Projects/AGENTS.md` (mtime 2026-05-13, ~4.8 KB)
- **Why qualifies:** Original technical specification authored by Maciej; governs how AI tooling behaves across all sub-projects.

---

## Tier 3 — Minor

### 10. creative — CI Workflow Fix (`context.repo.repo` for Label API)

- **Type:** Code / CI fix
- **Description:** Fixed a GitHub Actions workflow that called the Labels API with an incorrect repo reference; replaced with `context.repo.repo` so the workflow runs on any fork or rename.
- **Location:** `~/Projects/creative/` — commit `2cce704`
- **Why qualifies:** Small but original fix; eligible as creative authorship.

---

## Excluded (for traceability)

- `~/Projects/service-account-procedure.{html,md}` — April 2026, outside window.
- `~/Projects/copilot-config/`, `~/Projects/cursor-config/`, `~/Projects/directory-parser/` — May commits were PII scrub (`dbednarc` → `mmalysz` rename) only; no creative authorship.
- du-fwa-support routine case-management commits — operational, not creative.

---

## Submission Notes

- Submit each Tier 1 item individually (highest copyright value).
- Tier 2 may be bundled by theme (e.g., "Day2 SPIS Operational Documentation Suite") if the tool allows grouping.
- Tier 3 is optional — include only if monthly minimum requires it.
- Submission endpoint: Cisco Creative Work Tool per KB0066779 (Duo SSO required).
