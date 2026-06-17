---
title: JustLend sTRX Staking for AI Agents
description: AI-agent guide to JustLend sTRX staking, unstaking, exchange rate, rewards, withdrawal eligibility, and safety checks.
tags:
  - justlend
  - strx
  - staking
  - trx
  - liquid-staking
  - mcp
---

# JustLend sTRX Staking for AI Agents

Use this page when the user asks about staking TRX, receiving sTRX, unstaking, claiming rewards, or checking sTRX exchange rate and APY.

## Concept

sTRX is JustLend's liquid staking token for TRX. A user stakes TRX and receives sTRX. The sTRX exchange rate grows over time as staking and energy-rental rewards accrue.

Important user-facing points:

- sTRX is a TRC20 token.
- 1 sTRX is not always equal to 1 TRX; use the current exchange rate.
- Unstaking through JustLend has an unbonding period before TRX can be claimed.
- A user may alternatively swap sTRX on a third-party DEX, but that introduces market price and liquidity risk.

## Recommended MCP tools

Use the sTRX staking tool group in [`mcp_tools.md`](mcp_tools.md). Related routing pages are [Quickstart](quickstart.md), [MCP Safety](mcp_safety.md), and [Source of Truth](source_of_truth.md).

| Task | MCP tool | Notes |
|------|----------|-------|
| Dashboard / APY / exchange rate | `get_strx_dashboard` | Read-only staking overview. |
| User staking account | `get_strx_account`, `get_strx_balance` | Read-only wallet-specific status. |
| Withdrawal eligibility | `check_strx_withdrawal_eligibility` | Read-only pending withdrawal / claim readiness. |
| Stake TRX | `stake_trx_to_strx` | On-chain write; require HITL confirmation. |
| Unstake sTRX | `unstake_strx` | On-chain write; explain unbonding period first. |
| Claim rewards / available TRX | `claim_strx_rewards` | On-chain write; require HITL confirmation. |

## Safe staking workflow

1. Confirm network and wallet.
2. Query TRX balance.
3. Query current sTRX exchange rate and APY.
4. Explain that staking converts TRX into sTRX, not a fixed 1:1 redeemable balance.
5. Estimate energy/bandwidth and fees if available.
6. Require explicit confirmation.
7. Execute staking tool.
8. Verify wallet and sTRX balance.

## Safe unstaking workflow

1. Query sTRX balance and current exchange rate.
2. Explain the unbonding period and claim step.
3. Estimate expected TRX claim amount using the current exchange rate.
4. Require explicit confirmation.
5. Execute unstake tool.
6. Query withdrawal eligibility / pending withdrawals.
7. Tell the user when to claim.

## Chinese query mapping

- “质押 TRX” → stake TRX for sTRX.
- “sTRX 年化多少？” → query staking APY / exchange rate.
- “赎回 sTRX” → unstake sTRX; explain unbonding period.
- “什么时候能取回 TRX？” → check withdrawal eligibility.

## Precision rules

- TRX uses 6 decimals on-chain in sun.
- sTRX is an 18-decimal TRC20 token.
- Use MCP tool outputs or BigInt/string math for conversions.


## Source links

- [MCP Tool Catalog](mcp_tools.md) lists parameters, side effects, and annotations.
- [MCP Safety Policy](mcp_safety.md) defines confirmation rules for `stake_trx_to_strx`, `unstake_strx`, and `claim_strx_rewards`.
- [Common Questions](common_questions.md) includes bilingual routing examples for staking questions.
