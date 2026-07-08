---
title: JustLend AI Quickstart
description: Compact introduction to JustLend DAO for AI agents, including protocol scope, major workflows, and preferred integration surfaces.
tags:
  - justlend
  - quickstart
  - protocol-overview
  - ai-docs
  - mcp
---

# JustLend AI Quickstart

Use this page when the user needs a short protocol overview, feature routing, or a first answer about which JustLend document, OpenAPI endpoint, or MCP tool should be used.

JustLend DAO is a decentralized lending protocol on TRON based on the Compound V2 architecture. Users supply TRX or TRC20 assets to earn interest, borrow against collateral, stake TRX for sTRX, rent TRON Energy, and participate in governance.

## What JustLend includes

- **Supply and Borrow Market (SBM)**: deposit underlying assets, receive jTokens, borrow against collateral, repay debt, withdraw supplied assets.
- **sTRX staking**: stake TRX and receive sTRX. sTRX exchange rate grows as staking and energy-rental rewards accrue.
- **Energy Rental**: rent TRON Energy for transfers or contract calls instead of burning TRX.
- **Governance**: JST-based proposal and voting flows.
- **Mining rewards**: incentives for selected markets and reward tokens.

## Best entry points for agents

- For human-visible docs discovery: [`/llms.txt`](../../llms.txt)
- For one-shot context ingestion: [`/llms-full.txt`](../../llms-full.txt)
- For public HTTP API integration: [`justlend_apis.yaml`](../../developers/apis/justlend_apis.yaml)
- For contract addresses: [`contracts.json`](../../developers/contracts.json)
- For contract calls: [`developers/abis/`](../../developers/abis/jtoken.json)
- For wallet-aware agent operations: [`mcp_tools.md`](mcp_tools.md)

## Minimal decision tree

1. **Question only needs public data**: use OpenAPI or read-only MCP tools.
2. **Question needs portfolio analysis for an address**: use MCP `get_account_summary` or OpenAPI `/lend/account?address={address}`.
3. **Question asks to execute an action**: use MCP only, read [`mcp_safety.md`](mcp_safety.md), require human confirmation, and never ask for private keys in chat.
4. **Question asks for contract addresses**: use `contracts.json` and specify network.
5. **Question asks for terms such as collateral factor, exchange rate, or mantissa**: use [`glossary.md`](glossary.md) and the full glossary page.

## Important precision rules

- TRX is denominated in **sun** on-chain; 1 TRX = 1,000,000 sun.
- jTokens use **8 decimals**.
- Underlying assets use their own decimals: for example TRX and USDT use 6, BTC-style assets often use 8, ETH-style assets may use 18.
- Interest-rate and risk-parameter mantissas are commonly scaled by `1e18`.
- Do not submit transactions using floating-point JavaScript math. Use string amounts, BigInt, BigNumber, or MCP tools that already enforce precision-safe conversions.

## Safety rule

Read-only answers can cite docs and API data. Any workflow that signs or broadcasts a transaction must use MCP safety annotations, pre-flight checks, and explicit human-in-the-loop confirmation.


## Chinese / bilingual intent examples

- “JustLend 是什么？” → answer with the protocol overview and link to [Source of Truth](source_of_truth.md).
- “我要查市场 APY / TVL” → route to [Market Data](market_data.md) and MCP `get_market_data` / `get_all_markets`.
- “查看我的仓位 / 健康度 / 清算风险” → route to [Account Positions](account_position.md) and MCP `get_account_summary`.
- “帮我存款、借款、还款、赎回” → route to [Lending Workflows](supply_borrow_repay_withdraw.md) and [MCP Safety](mcp_safety.md).
- “质押 TRX / 租能量” → route to [sTRX Staking](strx_staking.md) or [Energy Rental](energy_rental.md).
