# Trust Tiers

Every entry in this index carries badges. They answer one question: **if this skill is
wrong, who finds out, and when?**

Skill directories elsewhere grade nothing. A skill that silently posts journal entries
and a skill that proposes them look identical in a bullet list. In accounting they are
not remotely the same product, and the difference is the whole review conversation with
your CPA.

Badges are assigned by reading the skill's own `SKILL.md`, not its marketing copy. A
badge is a claim we are willing to defend; where we could not verify one, the entry
says `UNGRADED` rather than guessing.

---

## Write authority — pick exactly one

| Badge | Meaning |
|---|---|
| `READ-ONLY` | Never mutates a system of record. Reads, computes, writes local artifacts only. |
| `PROPOSES-WRITES` | Can write to the ledger, but only through an explicit per-item or per-batch confirmation. Drafting a file for manual import also lives here. |
| `WRITES-DIRECT` | Writes to the system of record without a mandatory confirmation step. Use with care; we label it, we don't hide it. |

`READ-ONLY` is not a consolation prize. For close work it is usually the correct
design, and it is the one that survives an audit conversation.

## Money movement

| Badge | Meaning |
|---|---|
| `MOVES-MONEY` | Can transfer funds. Not a ledger write — an irreversible movement of real money out of a real account. Nothing else in this rubric matters as much, so it sits on its own and is never implied by a write-authority badge. |

## Evidence discipline

| Badge | Meaning |
|---|---|
| `DETERMINISTIC-MATH` | Figures are produced by a script over the data. The model writes the layout, never the numbers. |
| `TIE-CHECKED` | Ends in a computed proof — a difference that must be zero, a schedule that must roll, a cross-foot that must balance. Red until it passes. |
| `EVIDENCE-GATED` | Refuses to assert a conclusion the underlying data does not support. Distinguishes *explained* (evidence) from *attributed* (someone said so). |
| `PROVENANCE-STAMPED` | Every output figure carries its source and as-of date. |
| `INJECTION-AWARE` | Treats retrieved content — memos, customer names, product descriptions — as data to analyse, never as instructions to follow. Ledgers are full of free text written by outsiders; a skill that reads it without saying this is trusting it. |

## Judgment and control

| Badge | Meaning |
|---|---|
| `HUMAN-APPROVAL` | Has at least one hard checkpoint where the run stops for a person. |
| `MATERIALITY-AWARE` | Reads a threshold and behaves differently above and below it, instead of treating a $12 variance like a $120,000 one. |
| `PII-MINIMISING` | States what personal data it will not touch. Payroll and A/R skills sit next to SSNs, tax identifiers and bank details; one that refuses to collect them in chat and routes the user to a secure surface is making a commitment worth recording. |
| `AUDIT-TRAIL` | Persists its workpaper — proof, schedule, or summary — to a durable location, not just the chat. |
| `POLICY-CAPTURING` | Turns recurring judgment calls into written decision records so next period isn't re-litigated. |

## Blast radius

| Badge | Meaning |
|---|---|
| `CLIENT-FACING` | Produces output intended to leave the building. Must also carry `NO-AUTO-SEND` or `SENDS-EXTERNALLY`, so the reader never has to guess which. |
| `NO-AUTO-SEND` | Drafts only — will not transmit to a third party itself. |
| `SENDS-EXTERNALLY` | Transmits to someone outside the business — an email to a customer, a filing, a message. The opposite of `NO-AUTO-SEND`, and never implied: a skill carries one or the other, never neither, once it produces outward-facing content. |
| `STATEFUL` | Carries state across sessions. Re-reads its own state file rather than trusting conversation memory. |

## Disclosure

| Badge | Meaning |
|---|---|
| `SENDS-TELEMETRY` | Transmits something about the session to the vendor as a normal part of running — the user's prompt, the model, the client, a session id. Not a criticism, and often how a vendor keeps its docs current. It is recorded because a prompt in this domain can carry a client's financial position, and the reader should decide rather than discover. |

## Status

| Badge | Meaning |
|---|---|
| `GRADED` | A human read the source and assigned badges. `last_graded` is the date. |
| `NEEDS-RE-GRADING` | Upstream `SKILL.md` changed since the last grading. The badges below it are stale until someone re-reads it. |
| `UNGRADED` | Listed, not yet assessed. Treat badges as absent, not as passing. |
| `STALE` | `last_graded` is more than 180 days old. |

---

## The re-grading rule

A grade is a claim about a specific version of a file. When upstream changes the file,
the claim expires.

`scripts/check_drift.py` hashes each pointed-to `SKILL.md` daily. A changed body flips
the entry to `NEEDS-RE-GRADING` on `main` at once, and opens an issue linking the
upstream diff, with `MOVES-MONEY` and `WRITES-DIRECT` entries listed first. **The bot
never re-grades** — it only tells a person their judgment expired. Expiring a grade only
ever lowers a claim, so it ships without review; restoring one is a human's pull request.

The plugin carries this through to the answer. Every entry shows the `SKILL.md` hash it
was graded against and whether its grade is current, and each vendor page lists the
entries whose grade is not. The plugin never recommends a `MOVES-MONEY` or
`WRITES-DIRECT` skill whose grade is not current, and the build refuses to ship a
`GRADED` upstream entry that has no recorded hash.

That is the entire point of this index. The list is cheap; the grade is the product.

## Platform compatibility

Each entry carries a compatibility row. Values are derived from a stated rule, not from
running every skill on every platform, and each row says which:

- `verified: true` — someone ran it there.
- `verified: false` — inferred from the skill's shape. Skills with a `scripts/`
  directory need an agent that executes code; skills relying on slash-command
  invocation or `argument-hint` frontmatter degrade to plain instructions elsewhere.

We would rather publish an honest inference than an unmarked guess.
