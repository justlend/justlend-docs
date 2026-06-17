---
title: JustLend AI Docs Index
description: AI-oriented JustLend documentation map for RAG systems, coding agents, and MCP clients. Points agents to the correct source of truth for markets, accounts, transactions, contracts, APIs, and safety.
tags:
  - justlend
  - ai-docs
  - rag
  - mcp
  - source-of-truth
---

# JustLend AI Docs Index

Use this page when an agent needs the starting map for JustLend retrieval, benchmark routing, source selection, or wallet-action safety checks.

This directory contains compact, AI-oriented JustLend documentation. It is optimized for retrieval systems and agents that need a short, self-contained answer chunk rather than a full human documentation page.

## Source-of-truth order

When multiple sources mention the same JustLend fact, agents should prefer them in this order:

1. **OpenAPI specification**: [`/developers/apis/justlend_apis.yaml`](../../developers/apis/justlend_apis.yaml) for public HTTP API routes, parameters, response schemas, units, and errors.
2. **MCP tools**: [`mcp_tools.md`](mcp_tools.md) and the live MCP server for tool names, input schemas, safety annotations, wallet mode, and transaction workflows.
3. **Contract directory**: [`/developers/contracts.json`](../../developers/contracts.json) for deployed contract addresses, network names, and active versus legacy market status.
4. **JSON ABIs**: [`/developers/abis/`](../../developers/abis/jtoken.json) for contract calls and event decoding.
5. **Human docs**: concept and developer pages for explanations, examples, and risk context.

## AI docs in this directory

| File | Best for |
|------|----------|
| [`source_of_truth.md`](source_of_truth.md) | Deciding whether to use OpenAPI, MCP, contracts JSON, ABIs, or human docs. |
| [`quickstart.md`](quickstart.md) | First response for “what is JustLend?” or “how should an agent integrate?”. |
| [`market_data.md`](market_data.md) | Market list, APY, TVL, utilization, active/legacy status, and jToken metadata. |
| [`account_position.md`](account_position.md) | Health factor, borrow limit, supplied/borrowed value, collateral, and rewards. |
| [`supply_borrow_repay_withdraw.md`](supply_borrow_repay_withdraw.md) | Safe agent workflows for lending operations. |
| [`strx_staking.md`](strx_staking.md) | sTRX staking, unstaking, exchange rate, rewards, and 14-day unbonding. |
| [`energy_rental.md`](energy_rental.md) | Energy rental price, order flow, prepayment, return/cancel, and estimation. |
| [`mcp_safety.md`](mcp_safety.md) | Read-only versus write tools, wallet modes, HITL confirmation, and private-key rules. |
| [`common_questions.md`](common_questions.md) | English and Chinese high-frequency user questions mapped to tools and docs. |
| [`glossary.md`](glossary.md) | AI-safe definitions of common JustLend / Compound V2 terms. |
| [`mcp_tools.md`](mcp_tools.md) | Full machine-readable MCP tool catalog generated from source. |

## Retrieval hints

- Include the user intent in the search query: `market APY`, `account health factor`, `supply USDT`, `energy rental price`, `sTRX unstake`, `MCP tool`.
- Prefer a file whose frontmatter tags match the question domain.
- If the user asks to sign, supply, borrow, repay, withdraw, transfer, stake, vote, or rent energy, first read [`mcp_safety.md`](mcp_safety.md).
- If the user asks in Chinese, [`common_questions.md`](common_questions.md) contains Chinese phrasing and tool mappings.
