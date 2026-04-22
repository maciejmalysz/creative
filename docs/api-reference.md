# Creative Work Tool — API reference

Captured live on 2026-04-22 against `https://cxpp-external-proxy-alln.cisco.com/creative-work-tool/`
(version `1.0.23-SNAPSHOT`).

All endpoints are relative to the base URL above. All require a valid Duo SSO
session cookie. All POST endpoints require a CSRF token issued per page load.

---

## Authentication

1. Open the tool in a browser → Duo SSO challenge → success.
2. The browser receives a session cookie scoped to
   `cxpp-external-proxy-alln.cisco.com`. The exact cookie name varies but
   typically includes `SESSION=…` and one or more `ITDC_…` cookies.
3. Every rendered page contains a hidden `_csrf` input. The same token is valid
   for every form on that page until session expiry.

**Capturing for scripts** (Chrome DevTools, Application tab):

```text
Application → Cookies → https://cxpp-external-proxy-alln.cisco.com
  → copy ALL cookies as one string: NAME1=VAL1; NAME2=VAL2; …

Elements → Ctrl-F "_csrf" → copy the value="..." attribute
```

Export as `CWT_COOKIE` and `CWT_CSRF` for the helper scripts.

---

## POST `/user-info-update`

Update reporter profile. Form-encoded.

| Field | Required | Notes |
|-------|----------|-------|
| `reporterName` | ✓ | Free text, full name |
| `organizationName` | ✓ | One of the `<option>` values, see below |
| `teamName` | ✓ | Cascades from org |
| `managerName` | ✓ | Cascades from team |
| `jobTitle` | ✓ | Cascades from team |
| `deliverableName` | ✓ | Default deliverable type |
| `_csrf` | ✓ | Page CSRF |

---

## POST `/creative-work-add` — Path A

`enctype=multipart/form-data`.

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `creativeWorkTitle` | ✓ | text | Title visible in the dashboard |
| `reporterName` | ✓ | text | Usually identical to profile |
| `organizationName` | ✓ | select | See dropdowns |
| `teamName` | ✓ | select | Cascades from org |
| `managerName` | ✓ | select | Cascades from team |
| `jobTitle` | ✓ | select | Cascades from team |
| `deliverableName` | ✓ | select | e.g. *Design Document*, *Code Contribution* |
| `url` | ✓ | url | Public/internal link to the work |
| `deliverableFileUpload` | optional | file | One or more files; synced to SharePoint |
| `_csrf` | ✓ | hidden | |

**Success**: 302 redirect back to dashboard, new row appears with status `Pending`.

---

## POST `/creative-work-github-add` — Path B

Form-encoded. Submitted from `#githubPrsForm` after the user ticks PRs.

| Field | Required | Notes |
|-------|----------|-------|
| `selectedPrs[]` | ✓ (≥1) | Repeated; each value encodes the PR (`<repo>#<number>` or full URL — server-decoded) |
| Org/team/manager/job/deliverable fields | ✓ | Same cascading set as Path A; pre-filled from profile |
| `acceptStatement` | ✓ | Checkbox confirming the statutory statement |
| `_csrf` | ✓ | |

**Server behaviour**: For each selected PR, the server fetches metadata via the
stored credential (PAT or OAuth) and creates one entry per PR with
`deliverableName=Code Contribution` (or whatever is set in the form).

**Listing range**: closed/merged PRs since the **26th of the previous month** —
hard-coded in the dashboard query and corresponds to the Polish payroll cutoff.

---

## POST `/status-update` (out of scope)

Used by managers to approve/decline. Not driven from this repo.

---

## POST `/github/disconnect` and `/github/authorize`

Manage the in-tool GitHub credentials. Driven from the profile UI; not used by
scripts.

---

## Dropdown values (captured 2026-04-22)

### `organizationName`

```
CX
Engineering, Enterprise Connectivity & Collaboration
Engineering, Infrastructure & Security
Engineering, Infrastructure Engineering
Finance
Operations
People, Policy & Purpose
SIA
Sales
Splunk Customer Success & Experience
Splunk Eng, Prod & Design
Splunk Go to Market Operations
…
```

### Cascading dropdowns

`teamName`, `managerName`, `jobTitle`, `deliverableName` are populated by
client-side JS (`application.js`) from a per-org dictionary fetched at page
load. They are dynamic — capture the live list from your own session before
hard-coding any values.

A helper:

```js
// In DevTools console on the dashboard:
copy(JSON.stringify({
  org: [...document.querySelectorAll('#organizationNameReportCreativeWork option')].map(o => o.value),
  // open the modal, pick your org first, then re-run for the rest:
  team: [...document.querySelectorAll('#teamNameReportCreativeWork option')].map(o => o.value),
  manager: [...document.querySelectorAll('#managerNameReportCreativeWork option')].map(o => o.value),
  job: [...document.querySelectorAll('#jobTitleReportCreativeWork option')].map(o => o.value),
  deliverable: [...document.querySelectorAll('#deliverableNameReportCreativeWork option')].map(o => o.value),
}, null, 2));
```

Stash the result in `~/.config/creative-work-tool/dropdowns.json` and pass to
the helper script via `--dropdowns ~/.config/creative-work-tool/dropdowns.json`.
