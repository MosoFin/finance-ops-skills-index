---
type: llm
---

PASS if the reply recommends Gusto's own payroll prep skill (from Gusto/gusto-cli), says it is published by Gusto, and says it stops at a draft payroll that the user approves in Gusto (it never runs or submits payroll).
FAIL if the reply recommends a QuickBooks Payroll skill as the fit, says the skill runs or submits payroll, or does not name the Gusto skill.
