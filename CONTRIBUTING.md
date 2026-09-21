# Contributing

The list is cheap. The grade is the product. Most of this document is about grading.

## Adding an entry

```bash
make setup                                                   # once
make add URL=https://github.com/owner/repo/tree/main/skills/x STAGE=3 AUTHORITY=first-party
```

That reads the upstream `SKILL.md` frontmatter and the repository licence, writes a
correctly-shaped entry to `data/sources/<system>/<id>.yml`, records its drift baseline,
and regenerates the docs. Commit the new file together with the rebuilt output — CI
rejects a pull request where they disagree.

**Skills are stored under the data source they read.** `SYSTEMS` decides the folder:
the first entry that is a real system rather than a file format. A skill that reads no
connected system — one that works from artifacts or files alone — lives in
`data/sources/_any/`. The build refuses to run if a file sits in the wrong folder.

Never create or edit a file under `skills/` or `connectors/`; both are generated, as is
`docs/CONNECTOR-TRACKER.md`. Connector pages come from `connectors.yml`, which stays a
single file: it is read as a set, and its `statuses` and `auth_models` are shared
vocabulary that would be duplicated 37 times if split.

`STAGE` is 0-7 (see `stages` in `data/meta.yml`) — roughly, when in the close you reach
for it. `AUTHORITY` is `first-party` when the organisation that owns the product
published the skill itself, `notable` for a widely-used author who is not the product
owner, `community` otherwise. Provenance is not quality, and neither is a grade.

A new entry may land as `status: UNGRADED` with just `id`, `title`, `origin`, `stage`,
`summary`, `systems`, `upstream`, and `license`. That is a real contribution — it puts
the skill on the map and starts the drift clock. Grading can follow.

## Systems and reachability

`systems:` on an entry must name a key in `connectors.yml`, which records whether that
data can actually be reached — and at what cost. The build fails on an unknown system
rather than silently rendering a blank row.

Reachability is not a grade and never substitutes for one. A `gated` or `declined`
system means the grading above it is academic until the access story changes; the entry
says so on its own page.

`connectors.yml` is derived from the Vertical Connector Survey and carries its research
date. Auth models change — re-verify a row against vendor documentation before relying
on it, and update the date when you do.

## Grading an entry

**Read the skill's own `SKILL.md`. Do not grade from its description, its README, or
its marketing.** A description says what the author wants the skill to be; the body says
what it does.

Work through it once and answer, in order:

1. **Write authority.** Does any step mutate a system of record? Is there a mandatory
   confirmation in front of it, in the instructions themselves rather than in the
   author's intent? Pick exactly one of `READ-ONLY`, `PROPOSES-WRITES`, `WRITES-DIRECT`.
2. **Where do the numbers come from?** If a figure is produced by a script over real
   data, `DETERMINISTIC-MATH`. If the model may state a number it did not compute, the
   badge does not apply — no matter how careful the prose sounds.
3. **How does it end?** A computed proof that must balance, roll, or reach zero earns
   `TIE-CHECKED`. "Summarise the results" does not.
4. **What does it refuse?** Explicit instructions to ask rather than guess, or to
   distinguish evidence from assertion, earn `EVIDENCE-GATED`.
5. **Does it know what matters?** A threshold that changes behaviour earns
   `MATERIALITY-AWARE`. A number mentioned once and never used does not.
6. **What survives the session?** Durable workpapers earn `AUDIT-TRAIL`; re-read state
   files earn `STATEFUL`; written decision records earn `POLICY-CAPTURING`.
7. **Who else sees the output?** Anything meant to leave the building is
   `CLIENT-FACING`, and must also be `NO-AUTO-SEND` — or flagged loudly if it is not.

Then fill in `inputs`, `outputs`, `never`, and `tier_notes`.

- **`inputs`** — every input, whether it is required, where it comes from, and what
  happens when it is missing. The fallback column is the useful one: a skill that stops
  and a skill that guesses are different products.
- **`outputs`** — what is produced, in what form, and where it lands. "Where it lands"
  must be a real path or destination.
- **`never`** — the limits stated in the skill itself. Quote its intent, don't invent
  reassurance.
- **`tier_notes`** — one line per non-obvious badge, pointing at the mechanism that
  earns it. This is what a reviewer checks your grading against.

Finish with `status: GRADED` and today's date in `last_graded`.

### When you cannot tell

Leave the badge off. `UNGRADED` is a fine outcome and an honest one. A badge that turns
out to be wrong is worse for every reader than a badge that was never claimed.

## Re-grading

When the daily job opens a **Re-grading required** pull request, an upstream `SKILL.md`
changed and every badge on that entry is now a claim about a file that no longer exists.

Open the linked upstream diff, re-read the body, correct the grading, set `status: GRADED`
and a fresh `last_graded`, then rebuild. Merging without re-reading defeats the entire
mechanism — it is the one shortcut this repository cannot tolerate.

Entries pass 180 days without re-grading are reported as `STALE` by the same job.

## Licensing

Nothing is vendored by default.

- **Restricted** (`proprietary-*`) — pointer only, always. `anthropics/skills` ships a
  per-skill `LICENSE.txt` reading *"All rights reserved"*; copying those files here would
  redistribute material this repository has no right to redistribute. CI enforces it.
- **Copyleft** (`agpl-3.0`, `gpl-*`, `mpl-2.0`) — pointer by default. Mirroring would
  relicense this index, which is a deliberate decision, not a default. `check_drift.py`
  refuses `mirror: true` here until someone allowlists it on purpose.
- **Permissive** (`mit`, `apache-2.0`, …) — may set `mirror: true` and be vendored under
  `vendor/<id>/`, with attribution generated into `THIRD_PARTY_NOTICES.md`.

If an upstream `LICENSE.txt` hash changes, the drift job raises it as a hard failure
ahead of everything else. Look at that first.
