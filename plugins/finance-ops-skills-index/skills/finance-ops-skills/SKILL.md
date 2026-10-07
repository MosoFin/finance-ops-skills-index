---
name: finance-ops-skills
description: Recommends graded agent skills for finance and business-operations goals — month-end close, bank reconciliation, categorizing transactions, chasing overdue invoices, paying bills, expense reports, accruals and journal entries, financial statements and board packs, budget vs actuals, cash forecasts, payroll, invoicing, reconciling Stripe/PayPal/Shopify payouts, CRM pipeline reporting. Use when the user wants to get one of these done with an agent, asks which skill or plugin to use, asks whether skills exist for QuickBooks, Xero, Stripe, PayPal, Square, Shopify, WooCommerce, BigCommerce, HubSpot or similar software, or asks whether a skill is safe to let near their books or money. Load it as soon as the user states such a goal, before asking them anything — it says which platforms to confirm and then recommends. Read-only; it never installs or runs the skills it recommends.
license: MIT
---

# Finance & ops skills index

Turns a user's finance or operations goal into a plan of indexed skills, one per step, each matched to the platforms the user actually uses and graded for how far it can be trusted.

Answer only from the reference files, never from memory. The skills belong to their publishers: say which one fits and how far it can be trusted, and leave the instructions to the skill itself.

## Step 1 — Confirm the user's platforms before recommending anything

Every skill in the index runs on specific systems. A skill for the wrong ledger is not a near match, it is wrong. So before naming any skill:

1. Work out which of these the goal depends on:
   - **Ledger / accounting**: QuickBooks, Xero, other
   - **Payments**: Stripe, PayPal, Square, other
   - **Store**: Shopify, WooCommerce, BigCommerce, Amazon, Etsy, other
   - **CRM**: HubSpot, other
   - **Payroll**: QuickBooks Payroll, Gusto, other
   - **Where files live**: Google Drive or Sheets, Excel, PDFs or CSV exports
2. Take a platform as confirmed only if the user named it in this conversation, or it is plainly visible in what they shared (a QuickBooks export, a Stripe payout report). Never assume one because it is common. QuickBooks is the most indexed, which is not a reason to assume the user is on it.
3. If a platform the goal depends on is not confirmed, ask before recommending. Ask once, about only the systems this goal needs, and offer the likely options. For example, for a bank reconciliation: "Which accounting system are your books in — QuickBooks, Xero or something else? And do you have a bank feed, or statements as PDF or CSV?"
4. If the user does not know or will not say, you may describe the plan's steps, but name skills only as "if you are on X" options, never as the recommendation.

## Step 2 — Find the goal

1. Read `references/GOALS.md`. Match the user's goal to one there by meaning, not wording.
2. If no goal fits, build the plan yourself from `references/CATALOG.md`, which lists every skill by close stage. Keep the steps in close-stage order.
3. If the goal is about one platform rather than a task ("what is there for Xero?"), read `references/<vendor>.md` instead. `references/INDEX.md` lists the vendors.

## Step 3 — Pick a skill for each step

For each step, go through its candidates in order and keep the first that passes every check:

1. **Runs on the user's systems.** Its "runs on" list includes a platform the user confirmed, or `any`, or a file format (`csv`, `pdf`, `excel`, `images`…) the user can export to. A skill that needs QuickBooks does not fit a Xero user, however good it is.
2. **Grade is current.** Skip any candidate marked "do not recommend". If a candidate's grade is not current, you may still name it, saying the vendor changed it after it was graded.
3. **Can be installed.** Prefer a public skill. A "Mosofin workspace only" skill is not publicly installable: name it as an option only when nothing public fits, and say it is workspace only.
4. **Least authority that does the job.** Between two that fit, prefer READ-ONLY over PROPOSES-WRITES over WRITES-DIRECT.

Open the vendor page (`references/<vendor>.md`) for each skill you recommend, and give its details from there.

If no candidate passes, the step is a gap. Say "no indexed skill covers this for <platform>" and give the step's gap note if it has one. Never stretch a near match across platforms.

## Step 4 — Answer with a plan

Start with the platforms you are recommending for, so the user can correct them. Then, for each step in order:

- the step and what it achieves, in one line
- the recommended skill, its publisher exactly as the "Publisher" or "by" line gives it, and its upstream link. Call a skill the vendor's own only when that line says so: a Mosofin or Apideck skill that runs on QuickBooks or Xero was not made by Intuit or Xero.
- its write authority: READ-ONLY, PROPOSES-WRITES, WRITES-DIRECT, or MOVES-MONEY. Put MOVES-MONEY and WRITES-DIRECT first in the line, and say what confirmation it asks for.
- any warning: grade not current, sends telemetry, workspace only

Then list the gaps together. End with the catalog date from the reference files, and say that the user installs each skill from its upstream link — this plugin installs and runs nothing.

Keep it short. For a goal with many steps, a table is clearer than paragraphs.

## When a grade is not current

Vendors edit their skills without notice. Each entry records which version of its `SKILL.md` was graded, and each vendor page lists under "Grades not current" any entry whose grade no longer matches what the vendor publishes.

- Check "Grade current" on every entry before recommending it. If it says NO, say the vendor has changed the skill (or it has not been re-read recently), that its badges describe an older version, and give the "Graded version" line.
- Never recommend an entry marked "do not recommend" as the best fit. These are skills that move money or write directly to the books, and their grade is out of date. Name it only if the user asks about it by name, with that warning, and suggest a current alternative if one exists.
- Never tell the user how to carry out a task inside a vendor's product. Say which skill fits and how far it can be trusted; the vendor's own skill, installed from the upstream link, holds the instructions and is kept up to date by the vendor.

## Rules

- If a vendor page says no vendor-published skills were found, say that plainly. Do not invent a skill, and do not present a community skill as official.
- If the user asks whether a specific skill is safe and it is not in the index, or they want a skill checked before installing, use the `vet-skill` skill in this plugin to read and grade it. Never guess a grade for an unindexed skill.
- A badge is the index's own grading, not the vendor's claim. Say which it is.
- You cannot install, run or verify a skill from this catalog. Give the upstream link and let the user install it themselves.
