---
title: JustLend Account Position Queries
description: How agents should query account supply, borrow, collateral, borrow limit, health factor, liquidation risk, and rewards for a TRON address.
tags:
  - justlend
  - account
  - position
  - health-factor
  - borrow-limit
  - liquidation
  - mcp
  - openapi
---

# JustLend Account Position Queries

Use this page when the user asks about a wallet's JustLend position, health factor, collateral, borrow limit, borrow capacity, risk value, supplied assets, borrowed assets, or rewards.

## Recommended MCP tool

Use `get_account_summary`.

Typical inputs:

- `address`: TRON Base58 address starting with `T`
- `network`: `mainnet` or `nile`, default `mainnet`

The answer should summarize:

- supplied markets and values
- borrowed markets and values
- collateral markets
- borrow limit or liquidity
- health factor or liquidation risk
- rewards, if available
- timestamp or block number, if available

## OpenAPI fallback

Use `GET /lend/account/{address}` from `https://openapi.just.network` for read-only integrations.

Schema: [`/developers/apis/justlend_apis.yaml`](../../developers/apis/justlend_apis.yaml)

## Interpretation rules

- A lower health factor or higher risk value means higher liquidation risk.
- A position can be supplied but not counted as collateral unless the market has been entered as collateral.
- Borrow capacity depends on supplied value, collateral factors, oracle prices, and existing borrow value.
- Liquidation risk changes when token prices, borrow balances, or interest rates change.
- Always state that the values are a snapshot and should be refreshed before taking action.

## Safe response template

When answering an account query, use this structure:

1. **Network and address** checked.
2. **Total supplied** and top supplied markets.
3. **Total borrowed** and top borrowed markets.
4. **Collateral / borrow limit / health factor**.
5. **Risk assessment**: safe, watch, high risk, or liquidatable if the source clearly supports that classification.
6. **Next actions**: repay, supply more collateral, withdraw cautiously, or no action required.

## Chinese query mapping

- “查一下这个地址的 JustLend 仓位” → `get_account_summary`
- “健康因子是多少？” → `get_account_summary`
- “还能借多少？” → `get_account_summary`; explain borrow capacity.
- “会不会被清算？” → `get_account_summary`; explain liquidation risk and refresh before action.
- “收益/奖励有多少？” → account summary + rewards tools if available.

## Safety note

Account queries are read-only. If the user asks to repay, withdraw, borrow, or supply based on the result, switch to the safe workflow in [`supply_borrow_repay_withdraw.md`](supply_borrow_repay_withdraw.md) and require explicit confirmation before any write transaction.


## Source links

- [Source of Truth](source_of_truth.md) explains when to use MCP versus OpenAPI.
- [MCP Tool Catalog](mcp_tools.md) lists `get_account_summary` and wallet-read tools.
- [MCP Safety Policy](mcp_safety.md) applies before acting on liquidation, repay, or withdraw recommendations.
