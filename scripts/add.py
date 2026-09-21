#!/usr/bin/env python3
"""Add a skill to the index from its GitHub URL.

    ./.venv/bin/python scripts/add.py \
        https://github.com/googleworkspace/cli/tree/main/skills/gws-docs \
        --stage 6 --authority first-party

Reads the upstream SKILL.md frontmatter and the repository licence, appends a
well-formed UNGRADED entry under the data source it reads, and records the drift
baseline. It
never assigns a trust tier — grading is a person's job (see CONTRIBUTING.md).
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import textwrap
import urllib.error
import urllib.request

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FILE_FORMATS = {"csv", "pdf", "word", "powerpoint", "images", "any", "excel"}
AGNOSTIC = "_any"
SPDX = {
    "Apache-2.0": "apache-2.0", "MIT": "mit", "AGPL-3.0": "agpl-3.0",
    "GPL-3.0": "gpl-3.0", "BSD-3-Clause": "bsd-3-clause", "MPL-2.0": "mpl-2.0",
    "ISC": "isc", "CC0-1.0": "cc0-1.0",
}

URL_RE = re.compile(
    r"github\.com/(?P<repo>[\w.-]+/[\w.-]+)"
    r"(?:/tree/(?P<ref>[^/]+)/(?P<path>.+?))?/?$"
)


def get(url: str, raw: bool = False):
    req = urllib.request.Request(url, headers={"User-Agent": "mosofin-skills-index"})
    req.add_header("Accept", "application/vnd.github.raw" if raw else "application/vnd.github+json")
    if tok := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {tok}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read()
        return body.decode() if raw else json.loads(body)
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            raise SystemExit("GitHub rate limit. export GITHUB_TOKEN=$(gh auth token)") from e
        return None


def frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def wrap(text: str, indent: str = "  ") -> str:
    one = " ".join(str(text).split())
    return "\n".join(textwrap.wrap(one, width=78, initial_indent=indent, subsequent_indent=indent))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url", help="GitHub URL of the skill directory (…/tree/<ref>/<path>)")
    ap.add_argument("--stage", type=int, required=True, help="0-7, see data/meta.yml")
    ap.add_argument("--authority", default="community", choices=["first-party", "notable", "community"])
    ap.add_argument("--origin", default="third-party")
    ap.add_argument("--id", help="override the entry id (default: directory name)")
    ap.add_argument("--systems", default="any", help="comma-separated")
    ap.add_argument("--no-refresh", action="store_true",
                    help="skip drift+build; use for bulk adds, then run them once at the end")
    args = ap.parse_args()

    m = URL_RE.search(args.url.strip())
    if not m or not m.group("path"):
        raise SystemExit("need a URL of the form https://github.com/<owner>/<repo>/tree/<ref>/<path>")
    repo, ref, path = m.group("repo"), m.group("ref"), m.group("path").rstrip("/")

    meta = yaml.safe_load((DATA / "meta.yml").read_text())
    existing = {f.stem for f in (DATA / "sources").glob("*/*.yml")}
    if args.stage not in meta["stages"]:
        raise SystemExit(f"stage must be one of {sorted(meta['stages'])}")

    skill_md = get(f"https://raw.githubusercontent.com/{repo}/{ref}/{path}/SKILL.md", raw=True)
    if skill_md is None:
        raise SystemExit(f"no SKILL.md at {repo}/{path}@{ref} — check the URL")
    fm = frontmatter(skill_md)

    sid = args.id or fm.get("name") or path.rsplit("/", 1)[-1]
    if sid in existing:
        raise SystemExit(f"id '{sid}' already exists — pass --id to disambiguate")

    meta = get(f"https://api.github.com/repos/{repo}") or {}
    spdx = (meta.get("license") or {}).get("spdx_id") or ""
    lic = SPDX.get(spdx)
    if not lic:
        lic = f"proprietary-{repo.split('/')[0].lower()}"
        print(f"note: no recognised SPDX licence on {repo} — recorded as `{lic}`, pointer-only.")

    summary = fm.get("description") or meta.get("description") or "TODO: one-line summary."
    systems = "[" + ", ".join(x.strip() for x in args.systems.split(",")) + "]"

    systems_list = [x.strip() for x in args.systems.split(",")]
    real = [x for x in systems_list if x not in FILE_FORMATS]
    src = real[0] if real else AGNOSTIC

    block = (
        f"id: {sid}\n"
        f"title: {fm.get('name', sid)}\n"
        f"origin: {args.origin}\n"
        f"authority: {args.authority}\n"
        f"stage: {args.stage}\n"
        f"summary: >-\n{wrap(summary, '  ')}\n"
        f"tiers: []\n"
        f"systems: [{', '.join(systems_list)}]\n"
        f'upstream: {{repo: "{repo}", path: "{path}", ref: "{ref}"}}\n'
        f"license: {lic}\n"
        f"mirror: false\n"
        f"status: UNGRADED\n"
    )

    dest = DATA / "sources" / src
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / f"{sid}.yml"
    out.write_text(block)
    yaml.safe_load(out.read_text())  # fail loudly rather than commit broken YAML

    print(f"added {sid} -> {out.relative_to(ROOT)}  (licence {lic}, UNGRADED)")
    if args.no_refresh:
        return 0
    for cmd in (["scripts/check_drift.py", "--write"], ["scripts/build.py"]):
        subprocess.run([sys.executable, str(ROOT / cmd[0]), *cmd[1:]], check=True)
    print(f"\nNext: grade it. Open skills/{sid}/README.md and follow CONTRIBUTING.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
