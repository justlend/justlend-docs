---
title: JustLend Supply, Borrow, Repay, and Withdraw Workflows
description: Safe AI-agent workflows for JustLend lending actions, including pre-flight checks, allowance checks, collateral checks, health-factor checks, and post-transaction verification.
tags:
  - justlend
  - supply
  - borrow
  - repay
  - withdraw
  - lending
  - safety
  - mcp
---

# JustLend Supply, Borrow, Repay, and Withdraw Workflows

Use this page when the user asks an AI agent to deposit, supply, borrow, repay, redeem, or withdraw assets on JustLend.

These are write operations. They can sign and broadcast TRON transactions that move real assets. Use MCP tools only, perform pre-flight checks, and require explicit human confirmation.

## General safety workflow

1. Confirm network: `mainnet` for real funds, `nile` for testing.
2. Confirm wallet mode: browser wallet is preferred; agent-wallet is local encrypted fallback.
3. Validate asset and market: use `get_market_data` or `get_supported_markets`.
4. Check account state: use `get_account_summary`.
5. Estimate energy and fees where possible.
6. Show a deterministic transaction summary to the user.
7. Require explicit confirmation before signing or broadcasting.
8. After transaction, verify with `get_account_summary` or transaction receipt tools.

## Supply workflow

Use when the user says “supply”, “deposit”, “存入”, or “存款”.

Recommended MCP flow:

1. `get_wallet_address`
2. `get_market_data`
3. Check token balance:
   - TRX market: `get_trx_balance`
   - TRC20 market: token balance tool
4. For TRC20 markets, check allowance before approval.
5. If allowance is insufficient, approve the exact amount unless the user explicitly chooses unlimited approval.
6. Call the supply tool.
7. Verify with `get_account_summary`.

Important: jTRX uses native TRX and has a different mint path than TRC20 jTokens.

## Borrow workflow

Use when the user says “borrow”, “借款”, or “借出资产”.

Recommended MCP flow:

1. `get_account_summary`
2. Confirm collateral markets are entered.
3. `get_market_data` for target borrow market.
4. Check borrow is not paused and liquidity is sufficient.
5. Project post-borrow health factor.
6. Refuse or warn if the projected risk is unsafe.
7. Call borrow tool only after user confirmation.
8. Verify with `get_account_summary`.

## Repay workflow

Use when the user says “repay”, “还款”, or “还清”.

Recommended MCP flow:

1. `get_account_summary` to find current borrow balance.
2. Check wallet balance of the underlying repay token.
3. Check/approve allowance for TRC20 repay assets.
4. For full repayment, use the MCP-supported full-repay path or sentinel handling rather than hand-building raw values.
5. Call repay tool.
6. Verify with `get_account_summary`.

## Withdraw workflow

Use when the user says “withdraw”, “redeem”, “取出”, or “赎回”.

Recommended MCP flow:

1. `get_account_summary`
2. Check market liquidity and withdraw/redeem availability.
3. Project post-withdraw health factor if the user has borrows.
4. Warn if withdrawing collateral increases liquidation risk.
5. Call withdraw/redeem tool after confirmation.
6. Verify with `get_account_summary`.

## Common mistakes to avoid

- Do not skip `enterMarkets` checks before borrowing.
- Do not confuse jToken units with underlying units.
- Do not use floating-point math for token amounts.
- Do not recommend unlimited approval unless the user explicitly accepts the risk.
- Do not submit mainnet transactions without a final human confirmation.
- Do not assume a market is active just because it exists; legacy markets may be queryable but closed to new supply/borrow.


## Source links

- [MCP Safety Policy](mcp_safety.md) is mandatory before `supply`, `borrow`, `repay`, `withdraw`, or `withdraw_all`.
- [MCP Tool Catalog](mcp_tools.md) lists parameters, side effects, and annotations for lending tools.
- [Account Positions](account_position.md) explains health factor and liquidation-risk checks.
