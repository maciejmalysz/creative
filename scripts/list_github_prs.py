#!/usr/bin/env python3
"""list_github_prs.py — Path B pre-flight: show what the tool will offer to import.

Mirrors the Creative Work Tool's query for the GitHub PR import dialog:
    is:pr is:closed author:@me closed:>=YYYY-MM-26
where YYYY-MM is the previous month.

Supports both github.com (default) and Cisco internal GitHub.

Usage:
    export GH_TOKEN="github_pat_…"          # fine-grained PAT, read PRs
    python3 list_github_prs.py --since-26th
    python3 list_github_prs.py --host wwwin-github.cisco.com --since-26th

Pure-stdlib.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request


def previous_month_26th(today: dt.date | None = None) -> dt.date:
    """Return the 26th of the previous calendar month (matches tool behavior)."""
    today = today or dt.date.today()
    first_of_this_month = today.replace(day=1)
    last_day_prev_month = first_of_this_month - dt.timedelta(days=1)
    return last_day_prev_month.replace(day=26)


def search_prs(host: str, token: str, since: dt.date) -> list[dict]:
    """Search closed PRs authored by the authenticated user since `since`."""
    api = "https://api.github.com" if host == "github.com" else f"https://{host}/api/v3"
    q = f"is:pr is:closed author:@me closed:>={since.isoformat()}"
    url = f"{api}/search/issues?q={urllib.parse.quote(q)}&per_page=100&sort=updated"

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "creative-work-prs/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["items"]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--host", default="github.com", help="github.com or wwwin-github.cisco.com")
    p.add_argument("--since-26th", action="store_true", help="Use the tool's default cutoff (26th of previous month)")
    p.add_argument("--since", help="ISO date YYYY-MM-DD; overrides --since-26th")
    p.add_argument("--json", action="store_true", help="Emit raw JSON instead of a table")
    args = p.parse_args()

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("ERROR: set GH_TOKEN (fine-grained PAT with read access to your PRs).", file=sys.stderr)
        return 2

    if args.since:
        since = dt.date.fromisoformat(args.since)
    elif args.since_26th:
        since = previous_month_26th()
    else:
        print("ERROR: pass --since YYYY-MM-DD or --since-26th", file=sys.stderr)
        return 2

    try:
        prs = search_prs(args.host, token, since)
    except urllib.error.HTTPError as e:
        print(f"GitHub API error: HTTP {e.code} {e.reason}", file=sys.stderr)
        if e.code == 401:
            print("Token rejected — check it has read access on the right org.", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(prs, indent=2))
        return 0

    if not prs:
        print(f"No closed PRs since {since} on {args.host}.")
        return 0

    print(f"\n{len(prs)} closed PR(s) since {since} on {args.host}:\n")
    print(f"{'CLOSED':<11} {'REPO':<40} {'#':<6} TITLE")
    print("-" * 100)
    for it in prs:
        repo = it["repository_url"].rsplit("/repos/", 1)[-1]
        closed = (it.get("closed_at") or "")[:10]
        num = f"#{it['number']}"
        title = it["title"][:55]
        print(f"{closed:<11} {repo:<40} {num:<6} {title}")
    print()
    print("These are the PRs the Creative Work Tool will offer in 'Import from GitHub'.")
    print("Tip: prefix titles with [creative] to make them easy to spot in the picker.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
