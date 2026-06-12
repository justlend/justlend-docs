---
title: JustLend AI Glossary
description: Compact AI-safe definitions for common JustLend and Compound V2 terms used by agents, APIs, contracts, and MCP tools.
tags:
  - justlend
  - glossary
  - compound-v2
  - jtoken
  - risk
  - ai-docs
---

# JustLend AI Glossary

Use this compact glossary when answering JustLend questions. For the full glossary, see [`/resources/glossary`](../../resources/glossary.md).

## jToken

A TRC20 receipt token received when a user supplies an underlying asset to a JustLend market. jTokens usually use 8 decimals. Their exchange rate to the underlying increases as interest accrues.

## Underlying asset

The asset supplied to or borrowed from a market, such as TRX, USDT, USDD, BTC, ETH, JST, SUN, or other TRC20 assets.

## Exchange rate

The conversion ratio between jTokens and the underlying asset. It changes over time as interest accrues.

## Collateral factor

The percentage of a supplied asset's value that can count toward borrow capacity. A higher collateral factor allows more borrowing but can increase liquidation risk.

## Borrow limit

The maximum value a user can borrow based on supplied collateral, collateral factors, and oracle prices.

## Health factor / risk value

A risk indicator for an account. It compares borrowed value against collateralized borrowing capacity. A worse value means higher liquidation risk. Always query live data before action.

## Liquidation

A permissionless process where an unhealthy borrower's debt is partially repaid by a liquidator, who receives discounted collateral. JustLend follows Compound V2-style liquidation mechanics.

## Close factor

The maximum portion of a single borrowed asset that a liquidator can repay in one liquidation transaction.

## Liquidation incentive

The discount or reward received by liquidators when they repay unhealthy debt and seize collateral.

## Reserve factor

The portion of borrower interest retained by protocol reserves instead of flowing to suppliers.

## Utilization

Borrowed liquidity divided by supplied liquidity. Higher utilization usually increases borrow APY and can increase supply APY.

## APY

Annual percentage yield. JustLend APY changes over time with utilization, rewards, staking yield, and governance parameters.

## Mantissa

A fixed-point scaled integer representation, commonly using `1e18` scale for rates and risk parameters.

## Sun

The smallest unit of TRX. 1 TRX = 1,000,000 sun.

## Active market

A market open for current supply/borrow operations, subject to pause flags and liquidity.

## Legacy market

A market that may remain queryable and allow users to unwind positions but is closed or paused for new supply/borrow activity.

## sTRX

JustLend's liquid staking token for staked TRX. It is a TRC20 token and uses an exchange rate against TRX.

## Energy Rental

A JustLend sub-protocol for renting TRON Energy for a period instead of burning or staking TRX directly.


## Tool/API mapping examples

| Term or user phrase | Use this first | Why |
|---------------------|----------------|-----|
| APY / TVL / utilization | MCP `get_market_data` or `get_all_markets`; OpenAPI [`justlend_apis.yaml`](../../developers/apis/justlend_apis.yaml) | Values change continuously and must be queried live. |
| Wallet health factor / risk value | MCP `get_account_summary`; [Account Positions](account_position.md) | Requires wallet-specific collateral and borrow data. |
| jToken address / decimals | [`contracts.json`](../../developers/contracts.json), [`developers/abis/`](../../developers/abis/jtoken.json), or MCP `get_supported_markets` | Prevents symbol-only assumptions. |
| Supply / borrow / repay / withdraw | [Lending Workflows](supply_borrow_repay_withdraw.md) and MCP `supply`, `borrow`, `repay`, `withdraw` | Write tools require pre-flight checks and confirmation. |
| sTRX exchange rate / staking APY | [sTRX Staking](strx_staking.md), MCP `get_strx_dashboard` | sTRX is exchange-rate based, not fixed 1:1. |
| Energy rental price | [Energy Rental](energy_rental.md), MCP `calculate_energy_rental_price` | Rental price and availability are live values. |

## Chinese aliases for retrieval

- 抵押率 / collateral factor: how much supplied value counts as borrow capacity.
- 借款额度 / borrow limit: maximum borrowable value from collateral.
- 健康度 / 清算风险 / health factor: account-level risk indicator; query live data.
- 存款凭证 / jToken: receipt token received after supplying an asset.
- 年化 / APY: live annualized yield; do not reuse stale examples.
- 利用率 / utilization: borrowed liquidity divided by supplied liquidity.
- 质押 TRX / sTRX: staking flow covered by [sTRX Staking](strx_staking.md).
- 租能量 / energy rental: energy order flow covered by [Energy Rental](energy_rental.md).

## Retrieval rule

For definitions, answer briefly from this glossary. For numbers, addresses, wallet state, or transaction actions, route to [Source of Truth](source_of_truth.md), [MCP Tool Catalog](mcp_tools.md), and [MCP Safety Policy](mcp_safety.md) before finalizing the response.
