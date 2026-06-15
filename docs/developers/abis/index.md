---
title: JSON ABI files
description: Machine-readable JSON ABIs for JustLend DAO contracts — jToken, Comptroller, Price Oracle, Interest Rate Model, governance, sTRX, WJST, TRC20, and Energy Rental. Use for contract calls and event decoding.
tags:
  - justlend
  - abi
  - contracts
  - events
  - ai-docs
---

# JSON ABI files

Machine-readable ABIs for JustLend DAO contracts. Use them for contract calls (encoding function inputs / decoding outputs) and for decoding on-chain events. Contract **addresses** live in [`contracts.json`](../contracts.json) (Mainnet + Nile, in Base58 / EVM `0x` hex / TRON `41` hex); this page only covers the **interface** definitions.

> These files are the same ABIs the MCP server ships in [`src/core/abis.ts`](https://github.com/justlend/mcp-server-justlend/blob/main/src/core/abis.ts). When the rendered docs and the JSON ever diverge, treat the JSON as authoritative.

## Catalog

| ABI | Contract | Use for |
|-----|----------|---------|
| [`jtoken.json`](jtoken.json) | jToken (Supply & Borrow Market) | `mint`, `redeem`, `borrow`, `repayBorrow`, `balanceOfUnderlying`, `exchangeRateCurrent`, interest accounting, and `Mint` / `Borrow` / `Repay` events. |
| [`jtrx-mint.json`](jtrx-mint.json) | jTRX `mint` (TRX-specific) | Payable `mint` entry point for the native-TRX market (TRX is sent as `callValue`, no `approve`). |
| [`jtrx-repay.json`](jtrx-repay.json) | jTRX `repayBorrow` (TRX-specific) | Payable `repayBorrow` / `repayAmount` for the native-TRX market. |
| [`comptroller.json`](comptroller.json) | Comptroller | `checkMembership`, `enterMarkets`, `collateralFactorMantissa`, `closeFactorMantissa`, `claimReward`, guardian pause flags. |
| [`interest-rate-model.json`](interest-rate-model.json) | Interest Rate Model | `getBorrowRate`, `getSupplyRate`, `baseRatePerBlock`, `multiplierPerBlock`, `jumpMultiplierPerBlock`. |
| [`price-oracle.json`](price-oracle.json) | Price Oracle | `getUnderlyingPrice(jToken)` for collateral and borrow valuation. |
| [`governor-alpha.json`](governor-alpha.json) | GovernorAlpha | Proposal lifecycle, `castVote`, `forVotes` / `againstVotes` / `abstainVotes`, `eta`, `endBlock`. |
| [`poly.json`](poly.json) | JST voting | `castVote`, `getVoteInfo`, `totalVote`, `surplusVotes`, `jstBalance` (JST-weighted voting helper). |
| [`strx.json`](strx.json) | sTRX (Staked TRX) | `deposit`, `exchangeRate`, `claimAll`, balances — liquid-staking accounting. |
| [`wjst.json`](wjst.json) | WJST (Wrapped JST) | `deposit`, `approve`, `allowance`, `balanceOf` — ERC20-style JST wrapper. |
| [`trc20.json`](trc20.json) | TRC20 (generic) | `approve`, `allowance`, `balanceOf`, `decimals`, `transfer` for any underlying TRC20 asset. |
| [`energy-market.json`](energy-market.json) | Energy Rental market | `getRentInfo`, rental / stable rates, `feeRatio`, order accounting. |
| [`energy-rate-model.json`](energy-rate-model.json) | Energy Rental rate model | `getRentalRate`, `totalDelegated`, `totalFrozen`. |

## Decoding events

Derive `topic0` at runtime from the canonical signature rather than hard-coding it — for example `keccak256("Mint(address,uint256,uint256)")`. The full per-contract event-signature table and indexing options (TronGrid event filter, self-hosted indexer, MCP `read_events`) are documented in [APIs §8 — Event-stream and indexing options](../apis.md#8-event-stream-and-indexing-options).

## For AI agents

- Use these ABIs together with addresses from [`contracts.json`](../contracts.json); never hard-code addresses from prose.
- Respect precision rules: jTokens always use **8** decimals; each underlying TRC20 uses its own `decimals`; mantissa-scaled fields (`exchangeRate`, `borrowIndex`, rates) are scaled by `1e18`. See [APIs §1.3–1.4](../apis.md#13-numeric-formats).
- For wallet-aware contract writes, prefer the [MCP server tools](../../ai_support/mcp_server.md) over raw ABI calls so that side-effect annotations and HITL confirmation apply.
