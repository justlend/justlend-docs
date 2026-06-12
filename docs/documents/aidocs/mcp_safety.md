---
title: JustLend MCP Safety Policy for AI Agents
description: Safety rules for JustLend MCP tools, including read-only vs write tools, destructive operations, wallet modes, private-key handling, and human-in-the-loop confirmation.
tags:
  - justlend
  - mcp
  - safety
  - hitl
  - wallet
  - destructive-tools
  - private-key
---

# JustLend MCP Safety Policy for AI Agents

Use this page before any JustLend MCP workflow that may sign or broadcast a transaction.

## Tool classes

JustLend MCP tools fall into three practical classes:

1. **Read-only tools**: query markets, account state, balances, blocks, prices, rewards, or supported networks. These do not move assets.
2. **Local state / interaction tools**: connect browser wallet, set wallet mode, set network, select active wallet. These change local configuration or start a browser interaction.
3. **On-chain write tools**: supply, borrow, repay, withdraw, approve, transfer, stake, unstake, vote, rent energy, return energy, deploy or write contracts. These may move assets or create obligations.

Use [`mcp_tools.md`](mcp_tools.md) for the generated side-effect class and annotation of each tool.

## Human confirmation rule

Before any on-chain write tool, the agent must show:

- network
- wallet address
- contract or market
- action name
- amount and units
- estimated fee / energy if available
- risks such as liquidation, approval allowance, or unbonding period
- whether it will sign and broadcast a transaction

Then ask for explicit confirmation.

## Private key rule

Never ask the user to paste a private key or seed phrase into chat or MCP tool arguments.

Allowed wallet modes:

- **Browser wallet mode**: recommended. TronLink or another browser wallet signs transactions. Private keys never leave the wallet.
- **Agent wallet mode**: encrypted local wallet managed by `@bankofai/agent-wallet`. Use CLI or local wallet management; do not pass private keys through MCP prompts.

## Approval rule

For TRC20 supply/repay flows:

- Check allowance first.
- Prefer exact-amount approval.
- Unlimited approval is opt-in only. Explain that it lets the spender contract use the full token balance until revoked.
- After a large one-time transaction, suggest revoking or reducing allowance if appropriate.

## Mainnet rule

For Mainnet:

- Treat all write actions as real-money actions.
- Do not continue after pre-flight failure or simulation `REVERT`.
- Re-query account state after transaction confirmation.

For Nile testnet:

- It is safe for testing flows, but contract availability and market lists may differ from Mainnet.

## Refusal / pause conditions

Pause and ask the user before proceeding if:

- network is unclear
- wallet address is unclear
- amount is ambiguous
- market is legacy/paused
- projected health factor is unsafe
- allowance request is unlimited and user did not explicitly choose it
- the transaction simulation fails
- the user asks for private-key handling in chat


## Tool mapping examples

| Workflow | MCP tool examples | Required safety handling |
|----------|-------------------|--------------------------|
| Market and APY lookup | `get_supported_markets`, `get_market_data`, `get_all_markets` | Read-only; cite live timestamp when available. |
| Account risk lookup | `get_wallet_address`, `get_account_summary`, `get_balances` | Read-only; never infer health from stale data. |
| Lending writes | `supply`, `borrow`, `repay`, `withdraw`, `withdraw_all` | Pre-flight, allowance check, explicit HITL confirmation. |
| sTRX writes | `stake_trx_to_strx`, `unstake_strx`, `claim_strx_rewards` | Explain exchange rate and unbonding / claim flow. |
| Energy rental writes | `rent_energy`, `return_energy_rental` | Confirm receiver, amount, duration, prepayment, and return rules. |
| Governance writes | `vote_for_proposal`, `cast_vote`, `withdraw_votes_to_jst` | Confirm proposal id, vote direction, lock/withdraw effect. |

## Source links

- [MCP Tool Catalog](mcp_tools.md) is the generated list of all tools and side-effect annotations.
- [Source of Truth](source_of_truth.md) explains when MCP should be used instead of OpenAPI.
- [Common Questions](common_questions.md) shows bilingual user intents that trigger write-tool safeguards.
