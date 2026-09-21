#!/usr/bin/env python3
"""Probe each connector's GitHub org for officially published agent skills.

    ./.venv/bin/python scripts/probe_skills.py           report
    ./.venv/bin/python scripts/probe_skills.py --write   refresh counts and dates

Two different jobs, deliberately split:

* **Known repos** — recount SKILL.md and refresh `skills_checked`. No judgment
  needed, so `--write` updates these in place.
* **New candidates** — repos whose name suggests agent tooling and which contain
  SKILL.md, in an org with none recorded. These are *reported only*. A name match
  is not a relevance match: probing `facebook` for Meta Ads surfaces
  `immersive-web-sdk`, which is WebXR and has nothing to do with advertising.
  A person decides.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONNECTORS = ROOT / "connectors.yml"
HINT = re.compile(
    r"(^|[-_])(ai|agent|agents|skill|skills|mcp|toolkit|plugin|plugins|cli|sdk)([-_]|$)", re.I
)


def token() -> str:
    if t := os.environ.get("GITHUB_TOKEN"):
        return t
    r = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
    return r.stdout.strip()


TOK = token()


def api(url: str):
    req = urllib.request.Request(
        url, headers={"Accept": "application/vnd.github+json", "User-Agent": "mosofin-skills-index"}
    )
    if TOK:
        req.add_header("Authorization", f"Bearer {TOK}")
    try:
        with urllib.request.urlopen(req, timeout=30) as h:
            return json.load(h)
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            raise SystemExit("GitHub rate limit. export GITHUB_TOKEN=$(gh auth token)") from e
        return e.code
    except Exception:
        return None


def count_skills(full: str) -> int:
    t = api(f"https://api.github.com/repos/{full}/git/trees/HEAD?recursive=1")
    if not isinstance(t, dict) or "tree" not in t:
        return 0
    return sum(1 for x in t["tree"] if x["path"].endswith("SKILL.md"))


def org_repos(org: str) -> list:
    for kind in ("orgs", "users"):
        r = api(f"https://api.github.com/{kind}/{org}/repos?per_page=100&sort=pushed")
        if isinstance(r, list):
            return r
    return []


def probe(item):
    cid, c = item
    org = c.get("github_org")
    if not org or org == "none-found":
        return cid, None, None, []
    known = c.get("skills_repo")
    recount = count_skills(known) if known and known != "none" else None
    found = []
    if not known or known == "none":
        for r in [r for r in org_repos(org) if HINT.search(r["name"])][:8]:
            n = count_skills(r["full_name"])
            if n:
                found.append((n, r["full_name"], r.get("stargazers_count", 0)))
    return cid, known, recount, sorted(found, reverse=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    conn = yaml.safe_load(CONNECTORS.read_text())
    targets = [(k, v) for k, v in conn["connectors"].items() if v.get("github_org")]
    today = __import__("datetime").date.today().isoformat()

    text = CONNECTORS.read_text()
    changed, new = [], []

    with ThreadPoolExecutor(max_workers=8) as ex:
        for cid, known, recount, found in ex.map(probe, targets):
            if known and known != "none" and recount is not None:
                was = conn["connectors"][cid].get("skills_published", 0)
                if recount != was:
                    changed.append(f"{cid}: {known} {was} -> {recount} skills")
                    if args.write:
                        text = re.sub(
                            rf"(^  {re.escape(cid)}:.*?\n    skills_published: )\d+",
                            rf"\g<1>{recount}", text, count=1, flags=re.S | re.M,
                        )
                if args.write:
                    text = re.sub(
                        rf'(^  {re.escape(cid)}:.*?\n    skills_checked: )"[^"]*"',
                        rf'\g<1>"{today}"', text, count=1, flags=re.S | re.M,
                    )
            for n, full, stars in found:
                new.append(f"{cid}: candidate {full} — {n} skills, {stars} stars")

    if args.write:
        CONNECTORS.write_text(text)
        yaml.safe_load(CONNECTORS.read_text())
        print(f"connectors.yml refreshed ({today})")

    for line in changed:
        print(f"CHANGED {line}")
    for line in new:
        print(f"NEW     {line}")
    if not (changed or new):
        print("no change")
    print("\nNEW rows are name matches, not relevance matches — review before adding.")
    return 1 if new else 0


if __name__ == "__main__":
    sys.exit(main())
