#!/usr/bin/env python3
"""submit_creative_work.py — Path A: direct POST to the Creative Work Tool.

Usage:
    python3 submit_creative_work.py --capture-help
    python3 submit_creative_work.py \
        --title "NSO Service Pack v2 design doc" \
        --url "https://wwwin-github.cisco.com/mmalysz/nso-svc/blob/main/docs/v2.md" \
        --org "CX" --team "CX EMEA" \
        --manager "First Last" \
        --job "Customer Delivery Architect" \
        --deliverable "Design Document"

Requires env vars (capture from your authenticated browser):
    CWT_COOKIE   Full cookie header for cxpp-external-proxy-alln.cisco.com
    CWT_CSRF     The _csrf token from any rendered form on the dashboard

Pure-stdlib — no pip packages.
"""
from __future__ import annotations

import argparse
import os
import sys
import urllib.parse
import urllib.request
import uuid

BASE = "https://cxpp-external-proxy-alln.cisco.com/creative-work-tool"
SUBMIT_URL = f"{BASE}/creative-work-add"

CAPTURE_HELP = """\
How to capture CWT_COOKIE and CWT_CSRF (one-time per Duo session):

1. Open https://cxpp-external-proxy-alln.cisco.com/creative-work-tool/
   in Chrome. Complete Duo SSO so you see the dashboard.

2. F12 → Application → Cookies → https://cxpp-external-proxy-alln.cisco.com
   Right-click any cookie → "Copy as cURL" OR copy each cookie name=value
   pair joined by "; ". Example:
       SESSION=abc123; ITDC_AUTH=xyz789

3. F12 → Elements → Ctrl-F "_csrf" → copy the value="..." attribute.
   Example: fa38c8ee-f474-44cc-88fa-09298a459867

4. Export both:
       export CWT_COOKIE='SESSION=abc123; ITDC_AUTH=xyz789'
       export CWT_CSRF='fa38c8ee-f474-44cc-88fa-09298a459867'

The session typically lasts the rest of your work day. When you get a 302 to
the SSO URL or a 403, repeat from step 1.
"""


def build_multipart(fields: dict[str, str]) -> tuple[bytes, str]:
    """Build a minimal multipart/form-data body. Returns (body, content_type)."""
    boundary = f"----CWTBoundary{uuid.uuid4().hex}"
    lines: list[bytes] = []
    for name, value in fields.items():
        lines.append(f"--{boundary}".encode())
        lines.append(f'Content-Disposition: form-data; name="{name}"'.encode())
        lines.append(b"")
        lines.append(str(value).encode("utf-8"))
    lines.append(f"--{boundary}--".encode())
    lines.append(b"")
    body = b"\r\n".join(lines)
    return body, f"multipart/form-data; boundary={boundary}"


def submit(args: argparse.Namespace) -> int:
    cookie = os.environ.get("CWT_COOKIE")
    csrf = os.environ.get("CWT_CSRF")
    if not args.dry_run and (not cookie or not csrf):
        print(
            "ERROR: CWT_COOKIE and CWT_CSRF must be set. "
            "Run with --capture-help for instructions.",
            file=sys.stderr,
        )
        return 2
    if args.dry_run:
        cookie = cookie or "<not set — dry run>"
        csrf = csrf or "dryruncsrftoken"

    fields = {
        "_csrf": csrf,
        "creativeWorkTitle": args.title,
        "reporterName": args.reporter,
        "organizationName": args.org,
        "teamName": args.team,
        "managerName": args.manager,
        "jobTitle": args.job,
        "deliverableName": args.deliverable,
        "url": args.url,
    }

    body, ctype = build_multipart(fields)

    req = urllib.request.Request(
        SUBMIT_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": ctype,
            "Cookie": cookie,
            "Referer": f"{BASE}/",
            "Origin": "https://cxpp-external-proxy-alln.cisco.com",
            "User-Agent": "creative-work-submit/1.0 (+https://github.com/maciejmalysz/creative)",
        },
    )

    if args.dry_run:
        print("DRY RUN — would POST to:", SUBMIT_URL)
        for k, v in fields.items():
            shown = v if k != "_csrf" else f"{v[:8]}…"
            print(f"  {k}: {shown}")
        return 0

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            location = resp.headers.get("Location", "")
    except urllib.error.HTTPError as e:
        # 302 is success here — urllib treats it as redirect by default
        if e.code in (301, 302, 303):
            location = e.headers.get("Location", "")
            print(f"OK ({e.code}) — redirected to {location}")
            return 0
        print(f"HTTP {e.code}: {e.reason}", file=sys.stderr)
        if e.code in (401, 403):
            print(
                "Likely an expired Duo session. Refresh in browser and re-export "
                "CWT_COOKIE / CWT_CSRF.",
                file=sys.stderr,
            )
        return 1
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        return 1

    print(f"OK ({status}) — {location or 'submitted'}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--capture-help", action="store_true", help="Print cookie/CSRF capture instructions and exit.")
    p.add_argument("--title", help="Creative work title")
    p.add_argument("--url", help="Link to the work")
    p.add_argument("--reporter", help="Reporter full name (default: from $USER_FULL_NAME or git user.name)")
    p.add_argument("--org", help="Organization name (exact dropdown value)")
    p.add_argument("--team", help="Team name")
    p.add_argument("--manager", help="Manager full name")
    p.add_argument("--job", help="Job title")
    p.add_argument("--deliverable", help="Deliverable type (e.g. 'Design Document')")
    p.add_argument("--dry-run", action="store_true", help="Print the request, do not POST")
    args = p.parse_args()

    if args.capture_help:
        print(CAPTURE_HELP)
        return 0

    required = ["title", "url", "org", "team", "manager", "job", "deliverable"]
    missing = [f"--{r}" for r in required if not getattr(args, r)]
    if missing:
        print(f"ERROR: missing required arguments: {', '.join(missing)}", file=sys.stderr)
        print("Run with --capture-help for setup instructions.", file=sys.stderr)
        return 2

    if not args.reporter:
        args.reporter = os.environ.get("USER_FULL_NAME") or _git_full_name() or ""
        if not args.reporter:
            print("ERROR: --reporter not given and could not infer from git", file=sys.stderr)
            return 2

    return submit(args)


def _git_full_name() -> str | None:
    import subprocess
    try:
        out = subprocess.check_output(["git", "config", "--global", "user.name"], text=True).strip()
        return out or None
    except Exception:
        return None


if __name__ == "__main__":
    sys.exit(main())
