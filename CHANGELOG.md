# Changelog

All notable changes to the JustLend DAO documentation site.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Dates use `YYYY-MM-DD` (ISO 8601).

For the JustLend protocol itself, see governance proposals on [forum.justlend.org](https://forum.justlend.org) and on‑chain via `getActions(proposalId)` on the Governor contract.

---

## [Unreleased]

### Added — 2026-05-21 AI-readability v5 pass

- **`site_description` and `site_author`** in `mkdocs.yml` so every page renders a non-empty `<meta name="description">` and `<meta name="author">` (previously omitted on every page because both meta keys were missing).
- **Per-page YAML frontmatter** (`title` + `description`) on the 17 highest-value pages: all 8 user concept pages, `overview.md`, `tokenomics.md`, `apis.md`, `deployed_contracts.md`, `contracts_overview.md`, `sbm.md`, `ai_llms.md`, `mcp_server.md`, `justlend_skills.md`, plus `staked_trx.md` and `energy_rental.md` developer pages and the site root `index.md`. MkDocs / Material picks up `description` automatically into `<meta description>` and the JSON-LD `TechArticle.description`.
- **Explicit `# H1` headings** in the source Markdown of the 10 files that previously had none (`supply.md`, `borrow.md`, `withdraw.md`, `repay.md`, `risks.md`, `staked_trx.md`, `energy_rental.md`, `liquidations.md`, `overview.md`, `tokenomics.md`). HTML rendering was unaffected (Material synthesized the heading from nav), but raw-Markdown RAG loaders (which fetch `raw.githubusercontent.com/.../foo.md`) now see a heading anchor on every page.
- **"About this page" admonitions** on the 6 concept pages that lacked them (`supply.md`, `borrow.md`, `withdraw.md`, `repay.md`, `risks.md`, `staked_trx.md` (user), `energy_rental.md` (user)) plus upgraded admonitions on the two developer pages (`developers/staked_trx.md`, `developers/energy_rental.md`). Each banner restates protocol / network / units / cross-refs so any RAG chunk retrieved in isolation carries identity.
- **JSON-LD (`application/ld+json`)** in `docs/overrides/base.html` `<head>`, emitted on every page. Three nodes: an `Organization` for JustLend DAO, a `SoftwareApplication + FinancialProduct` for the protocol with `potentialAction` pointers to `/llms-full.txt`, `/developers/contracts.json`, and the OpenAPI YAML, and a per-page `TechArticle` carrying the page's description.
- **MkDocs `on_post_build` hook (`hooks/copy_dotfiles.py`)** that copies `docs/.well-known/` (and any future dotfile-rooted directory) into `site/.well-known/`. MkDocs's default file walker skips dotfile directories, so `/.well-known/security.txt` was returning 404 in production even though the file existed in the repo and was referenced from `llms.txt` / `robots.txt`.
- **`contracts.schema.json`** (JSON Schema 2020-12) — the `$schema` URL embedded in `contracts.json` now resolves to a real document. Schema enforces TRON Base58 / EVM 0x / TRON 41-hex address regexes and the per-record `network` enum.
- **Real landing content in `docs/index.md`** — previously a one-line meta-refresh tag with no body. AI crawlers landing on the site root now get protocol summary + curated entry points for users, developers, AI agents, governance, plus external links; browsers still 0-second redirect via meta-refresh + canonical.
- **Snapshot warning admonition** on the USD cost tables in `getting_started/concepts/energy_rental.md` (`§Cost Estimation`) — the example transactions and `$X.XX` numbers are historical and should not be fed into live pricing decisions.
- **Copy-pastable MCP install snippet** in `ai_support/justlend_skills.md` — a single `jq` one-liner that resolves `$(pwd)` and patches Claude Desktop's config in place, so AI agents that auto-execute the docs don't get stuck on `/ABSOLUTE_PATH_TO/` placeholders.

### Fixed — 2026-05-21 AI-readability v5 pass

- **`/.well-known/security.txt` 404 in production (P0).** The file was in `docs/.well-known/` and referenced by `llms.txt` and `robots.txt`, but MkDocs's default file walker skipped the dotfile directory. Fixed by the new `copy_dotfiles.py` hook.
- **Blocks-per-year math in `/llms-full.txt §7.4`.** Was `~10,512,000` (`365 × 86400 / 3`), which is off from the leap-year-averaged `10,517,760` (`365.25 × 86400 / 3`). Both numbers are now spelled out as approximations, with an explicit recommendation to prefer the API's pre-computed `apy` fields when precision matters.
- **`contracts.json` `_meta` block (P1).** `schema_version` bumped from `"1"` to semantic `"1.1.0"` with a `schema_version_policy` field explaining MAJOR / MINOR / PATCH semantics. Added `$schema` pointer to the new `contracts.schema.json`. Added an `address_formats` sub-block documenting each format's intended use case (Base58 for UI, hex_evm for cross-chain, hex_tron for TronGrid).
- **Backtick-colon parameter labels (P2).** `` `Supply APY:` `` (inline-code-then-colon) was tokenizing as one opaque code span; replaced with standard `**Supply APY:**` Markdown bold on `supply.md`, `borrow.md`, and `liquidations.md`. Also added a Borrow-Limit definition that was previously missing on `borrow.md`.
- **Broken link in `getting_started/concepts/liquidations.md` developer-reference footer** — `../../developers/apis/#3-supply-borrow-market` (which MkDocs flagged as unrecognized) → `../../developers/apis.md#3-supply-borrow-market`.

### Added — 2026-05-21 AI-data-consistency pass

- **`/llms-full.txt` snapshot metadata header** (`§0`): `last_generated`, `docs_commit`, `contracts_json_source`, `mcp_server_version` so consumers can detect staleness without diffing the body.
- **Homepage freshness admonition** in `getting_started/overview.md` covering protocol name, network (TRON Mainnet), market count (17 active + 6 legacy = 23), and pointers to the rendered footer date, `CHANGELOG.md`, and `/llms-full.txt`.
- **Self-contained "About this page" admonitions** at the top of `developers/contracts_overview.md` and `getting_started/concepts/liquidations.md` (P1 #4 fix from the v4 audit) so that RAG chunks retrieved in isolation still carry protocol + network + units context.
- **Structured contract overview table** in `developers/contracts_overview.md` (P1 #3) with one row per contract: address, upgradeable?, proxy mode, key functions, ABI link, doc link. Replaces the previous prose-only "navigation shell".
- **`<link rel="llms" href="/llms.txt">` discoverability hint** in `docs/overrides/base.html` `<head>` (P1 #5) plus `Sitemap`/`Allow: /llms.txt`-class entries already in `robots.txt`.

### Fixed — 2026-05-21 AI-data-consistency pass

- **Cross-page jToken count contradiction (P0 #1).** `ai_support/justlend_skills.md` previously titled its 9-row table "Supported Markets", which RAG chunks misread as the protocol's full market list, contradicting `llms-full.txt` (17 active + 6 legacy = 23). Renamed to "Featured Markets (CLI Quick Reference)" and reframed: the table is now explicitly a CLI shortcut subset, with the authoritative source-of-truth ordering (live API → `contracts.json` → `apis.md` §2) stated above it. `llms-full.txt §5.2` similarly hardened to cite the same single source of truth in-chunk.

### Added — prior to 2026-05-21
- `CHANGELOG.md` (this file).
- `mkdocs-git-revision-date-localized-plugin`: every page now shows last-updated date in the footer, sourced from git commit metadata.
- `AI / LLMs` navigation page listing `/llms.txt`, `/llms-full.txt`, OpenAPI, `contracts.json`, and JSON ABI endpoints for agent users.
- Machine-readable contract directory at `/developers/contracts.json`, including Mainnet and Nile addresses in Base58, EVM `0x` hex, and TRON-internal `41` hex.
- JSON ABI files under `/developers/abis/` for jToken, Comptroller, PriceOracle, TRC20, governance, WJST, sTRX, Energy Rental, and rate-model contracts.
- Nile testnet contract reference in `developers/deployed_contracts.md`, with the complete machine-readable list mirrored in `contracts.json`.
- Public API rate-limit guidance in `developers/apis.md`, `llms.txt`, `llms-full.txt`, and the OpenAPI `x-rate-limit` extension, including `429` retry behavior.
- Developer-reference cross-links from user concept pages to the corresponding contract functions and TronWeb examples.
- `/.well-known/security.txt` for automated security-contact discovery.
- MCP server docs synced to `@justlend/mcp-server-justlend` v1.0.7, including current dependency/runtime versions and precision-safe sTRX staking behavior.
- Resolved `_(see Tronscan)_` placeholders in `deployed_contracts.md`:
  - `jHTX` delegate implementation: `TJD7nb5Wq1P1rRi3Se2vLpLhksALdW8adb`.
  - `jUSDDOLD` underlying TRC20: `TPYmHEhy5n8TCEfYGqW2rPxsghSfzghPDn`.
- Re‑embedded interactive Swagger UI at the bottom of `developers/apis.md` (the 700‑line markdown reference still covers AI consumption; the embedded UI restores in‑page "Try it out").

### Removed
- Orphan documentation pages that were being indexed by `sitemap.xml` but rendered nearly empty: `developers/supply_and_borrow_market.md` and `governance/community_forum.md`.

### Fixed
- Removed duplicate ABI guidance from `developers/deployed_contracts.md` after adding local JSON ABI downloads.
- Added language tags to remaining unlabeled code fences in API and MCP docs.

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
