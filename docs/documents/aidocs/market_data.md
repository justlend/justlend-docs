---
title: JustLend Market Data for AI Agents
description: How agents should retrieve JustLend market lists, APY, TVL, utilization, prices, active/legacy status, jToken addresses, and underlying metadata.
tags:
  - justlend
  - market-data
  - apy
  - tvl
  - jtoken
  - openapi
  - mcp
---

# JustLend Market Data for AI Agents

Use this page when the user asks about supported markets, APY, TVL, utilization, prices, market status, jToken addresses, or underlying assets.

## Recommended sources

### MCP tools

- `get_supported_markets`: list available jToken markets, addresses, and underlying assets.
- `get_all_markets`: overview for all markets, including APY, TVL, utilization, and reward components.
- `get_market_data`: detailed information for a single market such as `jUSDT` or `jTRX`.
- `get_protocol_summary`: protocol-level market and risk configuration summary.

### OpenAPI

- `GET /lend/jtoken`: all jToken markets and live market data.
- `GET /lend/jtoken/{address}`: details for a specific jToken.
- `GET /lend/dashboard`: protocol-level totals.

Schema: [`/developers/apis/justlend_apis.yaml`](../../developers/apis/justlend_apis.yaml)

### Static address directory

- [`/developers/contracts.json`](../../developers/contracts.json): Mainnet and Nile addresses, active/legacy status, address formats.

## Answering market questions

When answering “which markets are supported?” include:

- network (`mainnet` or `nile`)
- market symbol (`jUSDT`, `jTRX`, etc.)
- underlying symbol (`USDT`, `TRX`, etc.)
- jToken address
- active or legacy status
- whether supply/borrow may be paused, if the source provides this status

When answering “what is the APY?” include:

- supply APY
- borrow APY
- mining or reward APY, if present
- total supply APY, if present
- timestamp or block context if available
- warning that APY changes with utilization and rewards

## Do not hard-code live data

Do not hard-code APY, TVL, utilization, liquidity, price, reward APY, or paused status from human docs. These values change. Query MCP or OpenAPI.

## Example user intents

| User question | Best source |
|---------------|-------------|
| “JustLend supports which markets?” | MCP `get_supported_markets` |
| “What is jUSDT supply APY?” | MCP `get_market_data` or OpenAPI `/lend/jtoken/{address}` |
| “Show all market TVL and utilization.” | MCP `get_all_markets` or OpenAPI `/lend/jtoken` |
| “What is the jUSDT contract address?” | `contracts.json` or MCP `get_supported_markets` |
| “Is jWBTT still active?” | `contracts.json` status + MCP market data |

## Chinese query mapping

- “JustLend 有哪些市场？” → `get_supported_markets`
- “USDT 存款 APY 多少？” → `get_market_data` with `market='jUSDT'`
- “查一下全部市场 TVL / 利用率” → `get_all_markets`
- “某个 jToken 地址是什么？” → `contracts.json` or `get_supported_markets`


## Source links

- [Source of Truth](source_of_truth.md) maps market questions to OpenAPI and MCP sources.
- [MCP Tool Catalog](mcp_tools.md) lists `get_supported_markets`, `get_market_data`, and `get_all_markets`.
- [AI Glossary](glossary.md) defines APY, utilization, jToken, and exchange-rate terms.
