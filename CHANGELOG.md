# Changelog

All notable changes to the JustLend DAO documentation site.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Dates use `YYYY-MM-DD` (ISO 8601).

For the JustLend protocol itself, see governance proposals on [forum.justlend.org](https://forum.justlend.org) and on‑chain via `getActions(proposalId)` on the Governor contract.

---

## [Unreleased]

### Added
- `CHANGELOG.md` (this file).
- `mkdocs-git-revision-date-localized-plugin`: every page now shows last-updated date in the footer, sourced from git commit metadata.
- Resolved `_(see Tronscan)_` placeholders in `deployed_contracts.md`:
  - `jHTX` delegate implementation: `TJD7nb5Wq1P1rRi3Se2vLpLhksALdW8adb`.
  - `jUSDDOLD` underlying TRC20: `TPYmHEhy5n8TCEfYGqW2rPxsghSfzghPDn`.
- Re‑embedded interactive Swagger UI at the bottom of `developers/apis.md` (the 700‑line markdown reference still covers AI consumption; the embedded UI restores in‑page "Try it out").

### Removed
- Orphan documentation pages that were being indexed by `sitemap.xml` but rendered nearly empty: `developers/supply_and_borrow_market.md` and `governance/community_forum.md`.

---

## [2026-05-20] — AI-readability overhaul (PR #51)

### Added
- **AI entry files** at the site root, served as `text/plain`:
  - `/llms.txt` — [llmstxt.org](https://llmstxt.org/) navigation index.
  - `/llms-full.txt` — condensed full-text snapshot for single‑fetch LLM consumption.
  - `/robots.txt` — explicit `Allow` for 20+ major AI crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended, etc.) and `Sitemap:` pointer.
- **`mkdocs-redirects`** configured for every legacy hyphenated URL (e.g. `/developers/supply-and-borrow-market/sbm/`) → current underscore URL, including the previously-404 `…/get-market-mining-apy-information`. Output is meta-refresh + `<link rel="canonical">`; major crawlers treat as 301-equivalent.
- **TronWeb call examples** in `developers/supply_and_borrow_market/sbm.md` (7 snippets), `developers/staked_trx.md` (4 snippets), and `developers/energy_rental.md` (4 snippets). Each includes a precision/unit admonition and the required pre-flight checks (e.g. `approve`, `enterMarkets`, `getAccountLiquidity`).
- **Machine-readable ABI canonical** reference in `ai_support/mcp_server.md` and `developers/deployed_contracts.md` pointing at [`mcp-server-justlend/src/core/abis.ts`](https://github.com/justlend/mcp-server-justlend/blob/main/src/core/abis.ts) and [`chains.ts`](https://github.com/justlend/mcp-server-justlend/blob/main/src/core/chains.ts).
- **HTX market** documented across all five docs (`deployed_contracts.md`, `apis.md` §2, `mcp_server.md`, `justlend_skills.md`, `llms-full.txt`).

### Changed
- **`developers/deployed_contracts.md`** restructured from bullet lists into tables with explicit "Network: TRON Mainnet" banner, Tronscan links on every row (ABI accessible via Contract tab), and precision/decimals admonition.
- **`developers/apis.md`** rewritten by upstream PR #50 from a single `<swagger-ui>` embed to a 700-line structured human-readable reference: response envelope (`{code, message, data}`), TRON Base58 address format, unit conventions (`*Rate` / `apy` as annualized decimals, `*Factor` ∈ [0, 1], jToken = 8 decimals), and `0x…` hex decoding for `/mining/distributions`.
- **`ai_support/mcp_server.md`** refreshed for `@justlend/mcp-server-justlend` v1.0.6: 59 tools (was 54), new categories (Mining & Rewards, Transfers, Wallet Mode), dual-mode signing (browser via TronLink TIP-6963 + agent-wallet), HTTP/SSE fail-closed `MCP_API_KEY` requirement.
- **`ai_support/justlend_skills.md`** updated to reflect the 9-tool read-only Skills MCP server, with cross-reference to `apis.md` §2 for the authoritative market list.
- **`developers/apis.md` §2 jToken Address Reference** now states "17 active + 6 legacy = 23 markets" with `jHTX` and four `*OLD` entries.

### Fixed
- **Market count consistency**: all five core docs (`deployed_contracts.md`, `apis.md`, `mcp_server.md`, `justlend_skills.md`, `llms-full.txt`) now report **17 active + 6 legacy = 23 markets**. Previously they reported 8 / 16 / 21 / 22 in different places.
- **Tool count consistency**: MCP server tool count is **59** everywhere (previously 9 / 54 / 59 in different files); Skills tool count is **9** everywhere.
- **`jUSDC` → `jUSDCOLD`** in `deployed_contracts.md`, `justlend_skills.md`, and `llms-full.txt` — the USDC supply/borrow market is closed but the contract is still queryable for read operations.
- **`jUSDJ` and `jWBTT`** marked as legacy (closed to new supply/borrow) across all docs.
- **`jUSDDOLD`** added to all docs as a legacy market with delegator `TX7kybeP6UwTBRHLNPYmswFESHfyjm9bAS`.
- **ETH / ETHB display-name swap** documented in `deployed_contracts.md`, `llms-full.txt`, and `justlend_skills.md`: the dApp UI now labels delegator `TR7BUFRQeq1w5jAZf1FKx85SHuX6PfMqsV` as "ETH" (formerly "ETHOLD") and delegator `TWBxQMb6RD3qmkXUXpNwVCYbL8SHNreru6` as "ETHB" (formerly "ETH"). On-chain addresses are unchanged.
- **CI workflow** (`.github/workflows/gh-pages.yml`) installs `mkdocs-redirects==1.2.2`; Chinese comments translated to English.

### AI-readability impact
External audit (`justlend-docs-ai-readability-report.md` series) tracked the project from **6.8 → 9.0 / 10** across this release (V1 → V3 reports). See `downloads/standards/` for the audit framework used.

---

## Earlier history

For documentation changes before 2026-05-20 (V1.0.4 / V1.0.5 / V1.0.6 MCP server refreshes, governance text fixes, API spec format updates), see the [GitHub releases](https://github.com/justlend/justlend-docs/releases) and `git log`.
