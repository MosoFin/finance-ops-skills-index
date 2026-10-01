---
name: finance-ops-skills
description: Look up agent skills published by vendors of finance and business-operations software (QuickBooks, Xero, Stripe, PayPal, Square, Shopify, WooCommerce, BigCommerce, HubSpot and others). Use when the user asks whether skills exist for a platform, which skill fits a bookkeeping, payments or store task, or how trustworthy a skill is. Read-only catalog lookup; it does not install or run the skills it lists.
license: MIT
---

# Finance & ops skills index

A read-only catalog of pointers to skills that vendors publish for their own software. Answer only from the reference files; never from memory.

## Steps

1. Read `references/INDEX.md` to see the vendors covered and how many skills are indexed for each.
2. Read `references/<vendor>.md` for the platform the user named. Use `references/_any.md` for skills that need no connected system (documents, spreadsheets, close checklists).
3. Match the user's task against each entry's summary and report the best fits.

## What to report for each match

- the skill id and what it does, in one line
- the upstream link, which is where the user gets the skill
- authority: first-party means the vendor published it; community means someone else did
- trust badges, especially whether it is READ-ONLY, PROPOSES-WRITES or WRITES-DIRECT
- the vendor's reachability, because a skill is only as useful as the data it can reach

## Rules

- If a vendor page says no vendor-published skills were found, say that plainly. Do not invent a skill, and do not present a community skill as official.
- Quote the "checked" date so the user knows how fresh the catalog is, and say entries may have changed upstream since.
- You cannot install, run or verify a skill from this catalog. Give the upstream link and let the user install it themselves.
- A badge is the index's own grading, not the vendor's claim. Say which it is.
- If nothing in the catalog fits, say so rather than stretching a near match.
