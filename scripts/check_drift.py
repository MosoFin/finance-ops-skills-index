#!/usr/bin/env python3
"""Compare every upstream pointer in sources.yml against its source repository.

A grade is a claim about one version of a file. When upstream changes that file,
the claim expires. This script detects that and nothing else — it never re-grades,
and it never rewrites a summary or a badge.

    ./.venv/bin/python scripts/check_drift.py            report only
    ./.venv/bin/python scripts/check_drift.py --write    update sources.yml in place

Exit codes: 0 nothing to do · 1 human attention required · 2 hard error.
Set GITHUB_TOKEN to lift the anonymous API rate limit.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources.yml"
API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
PERMISSIVE = {"mit", "apache-2.0", "bsd-3-clause", "bsd-2-clause", "isc", "cc0-1.0"}
# Open source, but strong copyleft: mirroring would relicense this index.
COPYLEFT = {"agpl-3.0", "gpl-3.0", "gpl-2.0", "lgpl-3.0", "mpl-2.0"}


def _get(url: str, raw: bool = False):
    req = urllib.request.Request(url, headers={"User-Agent": "mosofin-skills-index"})
    if raw:
        req.add_header("Accept", "application/vnd.github.raw")
    else:
        req.add_header("Accept", "application/vnd.github+json")
    if tok := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {tok}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read()
        return body if raw else json.loads(body)
    except urllib.error.HTTPError as e:
        return e.code
    except urllib.error.URLError as e:
        raise SystemExit(f"network error for {url}: {e}") from e


def latest_sha(repo: str, path: str, ref: str) -> str | int:
    r = _get(f"{API}/repos/{repo}/commits?path={path}&sha={ref}&per_page=1")
    if isinstance(r, int):
        return r
    return r[0]["sha"] if r else 404


def body_hash(repo: str, path: str, ref: str) -> str | int:
    r = _get(f"{RAW}/{repo}/{ref}/{path}/SKILL.md", raw=True)
    if isinstance(r, int):
        return r
    return "sha256:" + hashlib.sha256(r).hexdigest()[:16]


def license_hash(repo: str, path: str, ref: str) -> str | None:
    r = _get(f"{RAW}/{repo}/{ref}/{path}/LICENSE.txt", raw=True)
    if isinstance(r, int):
        return None
    return "sha256:" + hashlib.sha256(r).hexdigest()[:16]


def set_field(text: str, skill_id: str, key: str, value: str) -> str:
    """Rewrite one scalar field inside one skill block, preserving all formatting."""
    start = re.search(rf"^  - id: {re.escape(skill_id)}\s*$", text, re.M)
    if not start:
        return text
    nxt = re.search(r"^  - id: ", text[start.end():], re.M)
    end = start.end() + (nxt.start() if nxt else len(text) - start.end())
    block = text[start.end():end]
    line = f"    {key}: {value}\n"
    if re.search(rf"^    {re.escape(key)}:.*$", block, re.M):
        block = re.sub(rf"^    {re.escape(key)}:.*$", line.rstrip("\n"), block, count=1, flags=re.M)
    else:
        block = block.rstrip("\n") + "\n" + line
    return text[:start.end()] + block + text[end:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="update sources.yml in place")
    args = ap.parse_args()

    data = yaml.safe_load(SOURCES.read_text())
    text = SOURCES.read_text()
    today = dt.date.today().isoformat()
    regrade_after = data["meta"]["regrade_after_days"]

    changed: list[str] = []
    notices: list[str] = []
    fatal: list[str] = []

    for s in data["skills"]:
        up = s.get("upstream") or {}
        sid = s["id"]

        # Licence guard: a restricted pointer must never be mirrored.
        lic = str(s.get("license", "")).lower()
        if s.get("mirror") and lic in COPYLEFT:
            fatal.append(
                f"{sid}: mirror: true under copyleft licence `{lic}` — vendoring would "
                f"relicense this index. Decide deliberately, then allowlist it."
            )
        elif s.get("mirror") and lic not in PERMISSIVE:
            fatal.append(f"{sid}: mirror: true under licence `{lic}` — not permissive, refusing")
        if s.get("mirror") and (ROOT / "vendor" / sid).exists() is False:
            notices.append(f"{sid}: mirror: true but vendor/{sid} is missing")

        if "repo" not in up:
            # Local skill: only the staleness clock applies.
            if s.get("last_graded"):
                age = (dt.date.today() - dt.date.fromisoformat(str(s["last_graded"]))).days
                if age > regrade_after:
                    notices.append(f"{sid}: graded {age} days ago — past the {regrade_after}-day limit (STALE)")
            continue

        repo, path, ref = up["repo"], up["path"], up.get("ref", "main")
        sha = latest_sha(repo, path, ref)
        if sha in (403, 429):
            raise SystemExit(
                "GitHub rate limit reached. Set GITHUB_TOKEN and re-run — "
                "sources.yml was not modified.\n"
                "  export GITHUB_TOKEN=$(gh auth token)"
            )
        if sha == 404 or sha is None:
            fatal.append(f"{sid}: LINK ROT — {repo}/{path} not found on {ref}")
            continue
        if isinstance(sha, int):
            fatal.append(f"{sid}: GitHub API returned {sha} for {repo}/{path}")
            continue

        bh = body_hash(repo, path, ref)
        if isinstance(bh, int):
            fatal.append(f"{sid}: SKILL.md unreadable at {repo}/{path} (HTTP {bh})")
            continue

        lh = license_hash(repo, path, ref)
        if lh and s.get("license_hash") and lh != s["license_hash"]:
            fatal.append(f"{sid}: LICENCE CHANGED upstream — review before anything else")

        if s.get("skill_md_hash") != bh:
            if s.get("skill_md_hash") is None:
                notices.append(f"{sid}: first check — recording baseline {bh}")
            else:
                changed.append(
                    f"{sid}: SKILL.md changed upstream "
                    f"({s['skill_md_hash']} -> {bh}) — grade expired, re-read "
                    f"https://github.com/{repo}/commits/{ref}/{path}"
                )
            if args.write:
                text = set_field(text, sid, "skill_md_hash", bh)
                if s.get("status") == "GRADED":
                    text = set_field(text, sid, "status", "NEEDS-RE-GRADING")
        elif s.get("upstream_sha") != sha[:12]:
            notices.append(f"{sid}: sibling files changed, SKILL.md identical — grade stands")

        if args.write:
            text = set_field(text, sid, "upstream_sha", sha[:12])
            text = set_field(text, sid, "last_checked", today)
            if lh:
                text = set_field(text, sid, "license_hash", lh)

    if args.write:
        SOURCES.write_text(text)
        yaml.safe_load(SOURCES.read_text())  # fail loudly if the rewrite broke YAML
        print("sources.yml updated")

    for line in fatal:
        print(f"FATAL   {line}")
    for line in changed:
        print(f"REGRADE {line}")
    for line in notices:
        print(f"note    {line}")
    if not (fatal or changed or notices):
        print("no drift")

    if fatal:
        return 2
    return 1 if changed else 0


if __name__ == "__main__":
    sys.exit(main())
