---
title: JustLend Source of Truth for AI Agents
description: How agents should choose between JustLend OpenAPI, MCP tools, contracts.json, ABI JSON files, llms.txt, and human documentation.
tags:
  - justlend
  - source-of-truth
  - openapi
  - mcp
  - contracts
  - ai-docs
---

# JustLend Source of Truth for AI Agents

Use this page to decide which JustLend documentation or runtime source an AI agent should trust for a specific task.

## Priority order

1. **OpenAPI spec** — use for public read-only HTTP integrations.
   - File: [`/developers/apis/justlend_apis.yaml`](../../developers/apis/justlend_apis.yaml)
   - Base URL: `https://openapi.just.network`
   - Best for: market lists, account positions, protocol dashboard, mining rewards, response schemas, units, and error responses.

2. **MCP server tools** — use for agent workflows and wallet-aware actions.
   - Docs: [`mcp_tools.md`](mcp_tools.md), [`MCP Server`](../../ai_support/mcp_server.md)
   - Package: `@justlend/mcp-server-justlend`
   - Best for: account analysis, market queries, transaction pre-flight, supply, borrow, repay, withdraw, sTRX staking, energy rental, governance voting, transfers, and general TRON utilities.

3. **Contract directory** — use for deployed addresses.
   - File: [`/developers/contracts.json`](../../developers/contracts.json)
   - Schema: [`/developers/contracts.schema.json`](../../developers/contracts.schema.json)
   - Best for: Mainnet/Nile contract addresses, Base58/EVM/TRON-hex formats, active vs. legacy market status.

4. **JSON ABI files** — use for contract calls and event decoding.
   - Directory: [`/developers/abis/`](../../developers/abis/jtoken.json)
   - Best for: function signatures, event topics, jToken calls, Comptroller, PriceOracle, governance, sTRX, and Energy Rental contracts.

5. **Human documentation** — use for explanations and risk context.
   - Examples: [Supply](../../getting_started/concepts/supply.md), [Borrow](../../getting_started/concepts/borrow.md), [Common Pitfalls](../../developers/common_pitfalls.md), [Glossary](../../resources/glossary.md)
   - Best for: conceptual explanations, integration pitfalls, examples, and user education.

## Do not use stale assumptions

- Do not hard-code market counts, APYs, TVL, utilization, prices, rewards, or active/legacy status. Query OpenAPI or MCP.
- Do not infer token decimals from symbols. Use the token metadata from OpenAPI, contracts JSON, ABIs, or MCP tool output.
- Do not assume Mainnet when the user is testing. Ask for or default to `nile` only when the workflow is explicitly a testnet workflow.
- Do not use rendered HTML tables as the primary source for programmatic integrations; prefer YAML/JSON/tool output.

## Units and amounts — where to get self-describing values

The public HTTP API returns numbers in their on-chain form (e.g. base units, mantissa-scaled, annualized decimals) **without** an inline `_unit`/`decimals` envelope, by design. To interpret amounts correctly:

- **Need a ready-to-use amount?** Prefer **MCP tools** — balance/amount fields return a self-describing object `{ raw, _unit, decimals, display }` (e.g. `get_token_balance`, `get_trx_balance`), so you never re-apply decimals.
- **Using the HTTP API directly?** Read the unit and precision from the **OpenAPI spec**: each amount field carries structured `x-unit` / `x-decimals` extensions (and a prose description). Do not infer decimals from the symbol.
- **Quick reference:** jTokens always use **8** decimals; each underlying TRC20 uses its own `decimals`; `*Rate` / `apy` are annualized decimals (×100 for %); `exchangeRate` / `borrowIndex` and other mantissa fields are scaled by `1e18`. See [APIs §1.3–1.4](../../developers/apis.md#13-numeric-formats).

## Common source mapping

| User asks for | Use first | Fallback |
|---------------|-----------|----------|
| “What markets does JustLend support?” | MCP `get_supported_markets` or OpenAPI `/lend/jtoken` | `contracts.json` |
| “What is the APY / TVL / utilization?” | MCP `get_market_data` / `get_all_markets` | OpenAPI `/lend/jtoken` |
| “What is this address's health factor?” | MCP `get_account_summary` | OpenAPI `/lend/account?address={address}` |
| “Supply / borrow / repay / withdraw for me” | MCP guided prompt + tool | Human docs for explanation only |
| “What contract address should I use?” | `contracts.json` | MCP `get_supported_markets` / `chains.ts` |
| “How do I decode events?” | ABI JSON files | developer pages |
| “Is a transaction safe?” | MCP pre-flight tools + safety docs | human review |

## Answering rule for agents

When answering an integration question, include:

1. The recommended source or MCP tool.
2. Required inputs.
3. Important units and precision rules.
4. Whether the operation is read-only or signs/broadcasts a transaction.
5. Links to the relevant machine-readable source.


## Chinese source mapping

- “查市场 / APY / TVL / 利用率” → MCP `get_market_data` / `get_all_markets` or OpenAPI [`justlend_apis.yaml`](../../developers/apis/justlend_apis.yaml).
- “查我的仓位 / 健康度 / 清算风险” → MCP `get_account_summary` and [Account Positions](account_position.md).
- “存款 / 借款 / 还款 / 赎回” → MCP write tools plus [MCP Safety Policy](mcp_safety.md).
- “合约地址 / ABI / 事件解析” → [`contracts.json`](../../developers/contracts.json) and [`developers/abis/`](../../developers/abis/jtoken.json).
