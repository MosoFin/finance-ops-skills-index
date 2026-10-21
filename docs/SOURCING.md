# Sourcing rule

Which repository the index points to for a piece of software, and why.

The index exists to send people to the most authoritative way to use their
software with an agent. For each platform it looks in this order and stops at
the first step that finds something.

## 1. The vendor's own GitHub account

Look in the software vendor's own organisation (for QuickBooks, `intuit`; for
Xero, `XeroAPI`; for Square, `square`) for any of:

- agent skills (`SKILL.md`)
- an MCP server
- a Claude plugin, which bundles skills with a connection
- agents or a developer toolkit built for AI agents

Anything found here is indexed whatever its star count or age. Being published
by the vendor is the authority. Its age is shown, and its write and
money-movement badges say what it can do.

The vendor's parent platform counts when the software is built on it. For
WooCommerce, the official WordPress MCP Adapter qualifies.

## 2. A community repository, only if step 1 finds nothing

A repository not owned by the vendor qualifies only if both are true:

- **100 or more stars**
- **a commit within the last two weeks** at the time it is checked

Stars come from the repository page. The commit date comes from git itself.

The owner can list a repository that fails this test by explicit decision. Its
entry says so in its summary, for example the BigCommerce development plugin
(39 stars), listed because BigCommerce publishes nothing of its own.

## 3. Otherwise, a named gap

If neither step finds anything, the platform is listed with no recommendation,
and the plugin says so plainly rather than stretching a near match.

## Never

- **Apideck** (`apideck-libraries`). Its skills reach other vendors' software
  through Apideck's own paid unified API, are not published by those vendors,
  and the repository has too few stars to pass step 2.

## What an entry records

Each entry under `data/sources/<system>/` names its `kind` (`skill`,
`mcp-server`, `plugin`, `agent` or `toolkit`) and, under `upstream.file`, the
file its badges were read from: `SKILL.md` for a skill, usually `README.md` or
`agents/<name>.md` for the rest. `scripts/check_drift.py` hashes that file
daily, so a change to it expires the entry exactly as a changed `SKILL.md` does.

## Review log

| Date | Platform | Decision |
|---|---|---|
| 2026-10-21 | All | Apideck removed from BigCommerce, WooCommerce and Xero. |
| 2026-10-21 | BigCommerce | No official skill or MCP server. Community plugin `OrcaQubits/agentic-commerce-skills-plugins` (bigcommerce-commerce) listed by owner decision. Store data through the Mosofin gateway. |
| 2026-10-21 | WooCommerce | Added WooCommerce for Claude, both `woocommerce/agent-skills` skills, and the WordPress MCP Adapter. |
| 2026-10-21 | Xero | Added the official Xero MCP Server and Xero Agent Toolkit. |
| 2026-10-21 | QuickBooks | Added Intuit's QuickBooks Online MCP Server next to its Claude plugin. |
| 2026-10-21 | Square | Added Square's official MCP server. |
| 2026-10-21 | HubSpot | Added HubSpot's Sales plugin. `HubSpot/mcp-server` skipped: the repository is empty. |
| 2026-10-21 | PayPal | Added PayPal's agent toolkit and MCP server next to its AI-Toolkit plugin. |
| 2026-10-21 | Cross-platform | Added Anthropic's Month-End Closer and GL Reconciler agents. |
