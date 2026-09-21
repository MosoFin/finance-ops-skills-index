#!/usr/bin/env python3
"""Apply a grading to one skill file, preserving key order.

Grading is a human judgment recorded as data; this only writes it down.
    ./.venv/bin/python scripts/grade.py <id> <<'JSON'
    {"tiers": [...], "tier_notes": {...}, "inputs": [...], "outputs": [...], "never": [...]}
    JSON
"""
import datetime as dt, json, pathlib, sys, yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
ORDER = ["id","title","origin","authority","stage","summary","tiers","tier_notes",
         "systems","inputs","outputs","never","upstream","license","mirror",
         "status","last_graded","skill_md_hash","upstream_sha","last_checked","license_hash"]

def main() -> int:
    sid = sys.argv[1]
    grade = json.load(sys.stdin)
    hits = list((ROOT / "data" / "sources").glob(f"*/{sid}.yml"))
    if len(hits) != 1:
        print(f"expected one file for {sid}, found {len(hits)}", file=sys.stderr)
        return 1
    skill = yaml.safe_load(hits[0].read_text())
    skill.update(grade)
    skill["status"] = "GRADED"
    skill["last_graded"] = dt.date.today().isoformat()
    ordered = {k: skill[k] for k in ORDER if k in skill}
    ordered.update({k: v for k, v in skill.items() if k not in ordered})
    hits[0].write_text(yaml.safe_dump(ordered, sort_keys=False, allow_unicode=True, width=88))
    print(f"graded {sid}: {' '.join(grade.get('tiers', []))}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
