#!/usr/bin/env python3
"""Compare every upstream pointer against its source repository.

A grade is a claim about one version of a file. When upstream changes that file,
the claim expires. This script detects that and nothing else — it never re-grades,
and it never rewrites a summary or a badge.

    ./.venv/bin/python scripts/check_drift.py            report only
    ./.venv/bin/python scripts/check_drift.py --write    update the skill files in place

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
import time
import urllib.error
import urllib.request

import yaml

class Fatal(Exception):
    """An error, as opposed to a finding.

    Exit 1 means "upstream content changed, a human must re-grade". A bare
    SystemExit(message) also exits 1, so an error here used to be
    indistinguishable from a finding — the drift workflow read a rate-limit
    abort as drift and tried to open a re-grading pull request for it.
    Errors now exit 2.
    """


ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FILE_FORMATS = {"csv", "pdf", "word", "powerpoint", "images", "any", "excel"}
AGNOSTIC = "_any"
API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
MAX_RETRIES = 4
BACKOFF = 2.0          # seconds, doubled per retry
PACE = 0.08            # seconds between calls, to stay under the burst threshold

# Listed first in the re-grading issue: a stale grade on these is the costly kind.
HIGH_RISK = ("MOVES-MONEY", "WRITES-DIRECT")

PERMISSIVE = {"mit", "apache-2.0", "bsd-3-clause", "bsd-2-clause", "isc", "cc0-1.0"}
# Open source, but strong copyleft: mirroring would relicense this index.
COPYLEFT = {"agpl-3.0", "gpl-3.0", "gpl-2.0", "lgpl-3.0", "mpl-2.0"}


def _get(url: str, raw: bool = False, _attempt: int = 0):
    """One GitHub API call, with backoff for the secondary rate limit.

    GitHub answers 403 for two different things: the primary hourly limit
    (x-ratelimit-remaining: 0) and a secondary limit that throttles rapid
    bursts. This job makes three sequential calls per pointer with no pacing,
    which trips the secondary limit well before the hourly one — so treating
    every 403 as "out of quota" both misdiagnosed the failure and told the
    reader to set a token they had already set.
    """
    req = urllib.request.Request(url, headers={"User-Agent": "finance-ops-skills-index"})
    req.add_header("Accept", "application/vnd.github.raw" if raw else "application/vnd.github+json")
    if tok := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {tok}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read()
        return body if raw else json.loads(body)
    except urllib.error.HTTPError as e:
        if e.code not in (403, 429):
            return e.code
        hdr = e.headers
        if hdr.get("x-ratelimit-remaining") == "0":
            reset = hdr.get("x-ratelimit-reset", "")
            when = (
                dt.datetime.fromtimestamp(int(reset), dt.timezone.utc).strftime("%H:%M UTC")
                if reset.isdigit() else "unknown"
            )
            raise Fatal(
                f"GitHub hourly rate limit exhausted; resets at {when}. "
                + ("Token in use — wait for the reset." if os.environ.get("GITHUB_TOKEN")
                   else "Set GITHUB_TOKEN to raise the limit: export GITHUB_TOKEN=$(gh auth token)")
            )
        if _attempt >= MAX_RETRIES:
            raise Fatal(
                f"GitHub secondary rate limit after {MAX_RETRIES} retries on {url}. "
                "Re-run; the check is idempotent and resumes from the recorded baselines."
            )
        delay = float(hdr.get("retry-after") or BACKOFF * (2 ** _attempt))
        time.sleep(delay)
        return _get(url, raw, _attempt + 1)
    except urllib.error.URLError as e:
        raise Fatal(f"network error for {url}: {e}") from e


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


def skill_files() -> list[pathlib.Path]:
    return sorted((DATA / "sources").glob("*/*.yml"))


def save(path: pathlib.Path, skill: dict) -> None:
    """Rewrite one skill file.

    These files carry no comments — they are generated from a single mapping —
    so a plain dump is lossless. This replaces the previous approach of locating
    a skill's block inside one large file by scanning for the next `- id:`,
    which broke whenever an entry did not match the expected shape.
    """
    path.write_text(yaml.safe_dump(skill, sort_keys=False, allow_unicode=True, width=88))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="update the skill files in place")
    args = ap.parse_args()

    meta = yaml.safe_load((DATA / "meta.yml").read_text())
    loaded = [(f, yaml.safe_load(f.read_text())) for f in skill_files()]
    today = dt.date.today().isoformat()
    regrade_after = meta["meta"]["regrade_after_days"]
    dirty: dict[pathlib.Path, dict] = {}

    changed: list[str] = []
    notices: list[str] = []
    fatal: list[str] = []

    for path, s in loaded:
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
        if sha == 404 or sha is None:
            fatal.append(f"{sid}: LINK ROT — {repo}/{path} not found on {ref}")
            continue
        if isinstance(sha, int):
            fatal.append(f"{sid}: GitHub API returned {sha} for {repo}/{path}")
            continue

        time.sleep(PACE)
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
                risky = [b for b in HIGH_RISK if b in (s.get("tiers") or [])]
                changed.append(
                    (f"[{', '.join(risky)}] " if risky else "") +
                    f"{sid}: SKILL.md changed upstream "
                    f"({s['skill_md_hash']} -> {bh}) — grade expired, re-read "
                    f"https://github.com/{repo}/commits/{ref}/{path}"
                )
            if args.write:
                s["skill_md_hash"] = bh
                if s.get("status") == "GRADED":
                    s["status"] = "NEEDS-RE-GRADING"
                dirty[path] = s
        elif s.get("upstream_sha") != sha[:12]:
            notices.append(f"{sid}: sibling files changed, SKILL.md identical — grade stands")

        if args.write:
            s["upstream_sha"] = sha[:12]
            s["last_checked"] = today
            if lh:
                s["license_hash"] = lh
            dirty[path] = s

    if args.write and dirty:
        for path, skill in dirty.items():
            save(path, skill)
            yaml.safe_load(path.read_text())  # fail loudly rather than commit broken YAML
        print(f"{len(dirty)} skill file(s) updated")

    for line in fatal:
        print(f"FATAL   {line}")
    for line in sorted(changed, key=lambda l: not l.startswith("[")):
        print(f"REGRADE {line}")
    for line in notices:
        print(f"note    {line}")
    if not (fatal or changed or notices):
        print("no drift")

    if fatal:
        return 2
    return 1 if changed else 0


def _run() -> int:
    try:
        return main()
    except Fatal as e:
        print(f"FATAL   {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(_run())
