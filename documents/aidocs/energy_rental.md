---
title: JustLend Energy Rental for AI Agents
description: AI-agent guide to JustLend Energy Rental price estimation, rental orders, prepayment, return/cancel flows, and risk notes.
tags:
  - justlend
  - energy-rental
  - tron-energy
  - price-estimation
  - mcp
  - safety
---

# JustLend Energy Rental for AI Agents

Use this page when the user asks about renting TRON Energy, estimating rental cost, creating an energy rental order, returning energy, canceling an order, or checking rental status.

## Concept

JustLend Energy Rental lets users rent TRON Energy for a period instead of burning TRX or staking TRX themselves. It is often useful for TRC20 transfers and contract interactions.

Rental parameters typically include:

- rental amount in energy units
- rental duration
- receiving address
- prepayment / energy fee
- security deposit
- liquidation or penalty rules depending on the order state

## Recommended MCP tools

Use the Energy Rental MCP tool group in [`mcp_tools.md`](mcp_tools.md). Related routing pages are [Quickstart](quickstart.md), [MCP Safety](mcp_safety.md), and [Source of Truth](source_of_truth.md).

| Task | MCP tool | Notes |
|------|----------|-------|
| Dashboard / availability | `get_energy_rental_dashboard` | Read-only market status and summary. |
| Rental parameters | `get_energy_rental_params` | Read-only inputs for order planning. |
| Price calculation | `calculate_energy_rental_price`, `get_energy_rental_rate` | Always query live price before answering. |
| User orders | `get_user_energy_rental_orders`, `get_energy_rent_info` | Read-only order lookup. |
| Return information | `get_return_rental_info` | Check amount, order state, and return rules. |
| Create rental | `rent_energy` | On-chain write; require HITL confirmation. |
| Return energy | `return_energy_rental` | On-chain write; require HITL confirmation. |
| Lending energy estimate | `estimate_lending_energy` | Useful before supply/borrow/repay/withdraw. |

## Price estimation workflow

1. Ask for intended action or target energy amount.
2. If action is known, estimate required energy first.
3. Query current rental price using the MCP calculation tool.
4. Explain the cost components:
   - energy fee
   - security deposit
   - potential penalty / liquidation terms
5. State that prices and available energy change over time.

## Safe rental workflow

1. Confirm receiving address.
2. Validate address is a regular TRON account when required.
3. Confirm rental amount and duration.
4. Calculate price and show prepayment.
5. Require explicit confirmation.
6. Create the rental order using MCP.
7. Verify order status.

## User guidance

- For USDT transfers, energy needs differ depending on whether the receiver already has a token balance.
- Short rentals should be returned promptly when no longer needed.
- Do not assume historical price examples are current; always calculate live price.
- If the user only needs one transaction, compare rental cost with burning TRX, but use current chain data.

## Chinese query mapping

- “租能量多少钱？” → calculate energy rental price.
- “帮我租能量” → safe rental workflow.
- “USDT 转账需要多少能量？” → estimate energy; explain warm/cold receiver difference.
- “退还能量 / 取消订单” → query order then return/cancel via MCP.


## Source links

- [MCP Tool Catalog](mcp_tools.md) lists parameters, side effects, and annotations.
- [MCP Safety Policy](mcp_safety.md) defines confirmation rules for `rent_energy` and `return_energy_rental`.
- [Common Questions](common_questions.md) includes bilingual routing examples for energy rental questions.
