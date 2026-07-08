---
title: JustLend Common Questions for AI Agents
description: High-frequency English and Chinese JustLend questions mapped to the recommended MCP tools, OpenAPI endpoints, and documentation pages.
tags:
  - justlend
  - faq
  - common-questions
  - chinese
  - english
  - mcp
  - openapi
---

# JustLend Common Questions for AI Agents

Use this page when the user asks a natural-language JustLend question in English or Chinese and the agent needs to map it to the safest source, API, or MCP tool.

This page maps common user questions to the best JustLend source or MCP tool.

## Market questions

### What markets does JustLend support?

Use MCP `get_supported_markets`, or OpenAPI `GET /lend/jtoken`.

Answer with network, jToken symbol, underlying symbol, address, and active/legacy status.

Chinese: “JustLend 有哪些市场？”、“支持哪些币种？”

### What is the APY for jUSDT / jTRX / another market?

Use MCP `get_market_data` for one market or `get_all_markets` for all markets. For HTTP integration, use OpenAPI `GET /lend/jtoken` or `GET /lend/jtoken?address={jToken}`.

Chinese: “USDT 存款年化多少？”、“TRX 借款 APY 多少？”

## Account questions

### How do I check a JustLend account position?

Use MCP `get_account_summary` with the user's TRON address and network. For HTTP integration, use `GET /lend/account?address={address}`.

Chinese: “查一下这个地址的 JustLend 仓位”、“这个地址健康因子是多少？”

### Can this account be liquidated?

Use MCP `get_account_summary`. Explain liquidation risk using health factor, borrow limit, total borrow, collateral value, and current prices. State that it is a snapshot and should be refreshed before action.

Chinese: “会不会被清算？”、“风险值是多少？”

## Lending action questions

### Can you supply USDT / TRX for me?

Use the MCP supply workflow. First read [`mcp_safety.md`](mcp_safety.md), then check wallet, balance, market status, allowance if TRC20, and require confirmation.

Chinese: “帮我存入 USDT”、“把 TRX 存到 JustLend”。

### Can you borrow USDT?

Use the MCP borrow workflow. Check account summary, collateral markets, liquidity, borrow paused status, projected health factor, and require confirmation.

Chinese: “帮我借 USDT”、“还能借多少？”

### Can you repay or withdraw?

Use the MCP repay or withdraw workflow. Always check account summary first and verify post-transaction state.

Chinese: “帮我还款”、“取出抵押物”、“赎回 jToken”。

## sTRX questions

### What is sTRX and how do I stake TRX?

Use [`strx_staking.md`](strx_staking.md). Query current exchange rate and APY with MCP tools. Explain that unstaking has an unbonding period.

Chinese: “sTRX 是什么？”、“质押 TRX 年化多少？”、“什么时候能取回 TRX？”

## Energy Rental questions

### How much does it cost to rent energy?

Use MCP energy rental price calculation tools. Do not reuse stale examples as current prices.

Chinese: “租能量多少钱？”、“转 USDT 要多少能量？”

### Can you rent energy for me?

Use the safe rental workflow in [`energy_rental.md`](energy_rental.md). Confirm receiving address, energy amount, duration, price, and require confirmation.

Chinese: “帮我租能量”、“给这个地址租能量”。

## Contract / developer questions

### What contract address should I use?

Use [`contracts.json`](../../developers/contracts.json), specify network, and include Base58 plus hex format if relevant.

Chinese: “jUSDT 合约地址是什么？”、“Nile 测试网地址在哪？”

### How do I call or decode a contract?

Use JSON ABIs under [`/developers/abis/`](../../developers/abis/jtoken.json). For event indexing, see the developer API docs and common pitfalls.

Chinese: “怎么解析 Borrow 事件？”、“jToken ABI 在哪？”

## Safety questions

### Should I use browser wallet or agent wallet?

Browser wallet is recommended for most users because private keys stay in TronLink or another browser wallet. Agent wallet is for local encrypted automation. Never paste private keys or seed phrases into chat.

Chinese: “要不要导入私钥？”、“TronLink 和 agent wallet 哪个安全？”
