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
| 2026-10-21 | Google Ads | Added Google's official read-only `googleads/google-ads-mcp`. |
| 2026-10-21 | Amazon Seller | Added three skills from Amazon's official `amzn/selling-partner-agentic-toolkit`: month-end close, seller analytics, stockout prevention. |
| 2026-10-21 | Meta Ads | Nothing official on GitHub. Meta's hosted Ads MCP noted in the vendor page. Community candidates that pass step 2 (Ryze, Pipeboard) are paid hosted services; awaiting owner decision. |
| 2026-10-21 | TikTok Shop | Added as a platform. Nothing official; the only community repo passing step 2 (`xixihhhh/clipforge`) makes videos and does not read shop data, so it is a named gap. |
| 2026-10-27 | NetSuite | Added Oracle's Finance Analyst skill and SuiteSkills finance runbooks from `oracle/netsuite-suitecloud-sdk`. NetSuite AI Connector address from Oracle's documentation, unconfirmed. |
| 2026-10-27 | Zoho Books | Added Zoho's own Books plugin (built for Google Antigravity) and Zoho's hosted Books server. |
| 2026-10-27 | MYOB, FreshBooks, Sage, Wave | Nothing official on GitHub, no community repository passes step 2. MYOB's Claude rollout and Sage's Intacct server are announced without an address. |
| 2026-10-27 | Gusto | Added the three skills bundled in Gusto's own CLI (`Gusto/gusto-cli`); payroll is drafted, never run. |
| 2026-10-27 | Rippling, Deel, ADP, Paychex | No official repositories indexed. Deel's hosted server listed; Rippling's address is shown only in-product; `deel-public/deel-public-mcp` not confirmed as Deel's and can issue off-cycle payments, so skipped. |
| 2026-10-27 | Ramp | Added four finance skills from `ramp-public/skills` and the Ramp CLI (approves bills and reimbursements). Travel and agent-purchase skills not indexed. |
| 2026-10-27 | Expensify | Added both skills from Expensify's own plugin; both read-only. |
| 2026-10-27 | Brex, BILL, Navan | Nothing official on GitHub. Brex's hosted server (beta) listed; BILL's is documentation only; Navan's is announced without an address. |
| 2026-10-27 | Mercury | Added three skills from `MercuryTechnologies/mercury-skills` (no licence file) and the Mercury CLI, which can send payments. |
| 2026-10-27 | Airwallex | Added Airwallex's own AgentOS plugin; it refuses transfers and FX conversions. |
| 2026-10-27 | Plaid, Wise, Relay | Plaid's toolkit is sandbox-only developer tooling, not indexed. Nothing from Wise or Relay. |
| 2026-10-27 | eBay | Added eBay's own read-only API MCP server. |
| 2026-10-27 | Etsy, Klaviyo, Harvest, Jobber, ServiceM8 | Vendor-hosted servers recorded. Jobber's GitHub repository skipped: it ships a client secret in plain text. Etsy's server searches documentation only. |
| 2026-10-27 | Ecwid, Lightspeed, Clover, Clio, ServiceTitan, Housecall Pro, Toast, NCR Voyix | Re-checked; nothing official, no community repository passes step 2. |
