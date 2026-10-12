---
title: JSON ABI files
description: Minimal JSON interfaces for JustLend DAO contract integrations, with explicit network, provenance, and event-decoding limitations. These files are not complete deployment build artifacts.
tags:
  - justlend
  - abi
  - contracts
  - events
  - ai-docs
---

# JSON ABI files

These files are **minimal integration interfaces, not complete deployment build artifacts**. They encode/decode only the entries actually present in each JSON file. A function mentioned elsewhere in the documentation is not necessarily included, and a function-only file cannot decode events. Contract addresses live in [`contracts.json`](../contracts.json); a Mainnet interface must not be assumed to match Nile or a later implementation.

> These interfaces originated from the MCP server's [`src/core/abis.ts`](https://github.com/justlend/mcp-server-justlend/blob/main/src/core/abis.ts), with docs-local corrections described below. They are not guaranteed to remain byte-for-byte identical to the MCP package. Neither a prose page nor this subset overrides the ABI of the actual deployed implementation.

## Scope and provenance

The [machine-readable scope manifest](manifest.json) records the corrections checked on **2026-10-12**:

- **GovernorBravo:** Mainnet proxy `TEqiF5JbhDPD77yjEfnEMncGRZNDt2uogD` returned implementation `TUeNh9BsYK44XePmFAuKZWg2rJuU7bSt5u`. Input types and selected events were taken from that implementation's node ABI. `getReceipt` returns one tuple; its `bool / uint8 / uint96` components were expanded from the pinned official source because the node omits tuple components. This is not a bytecode-reproduced compiler artifact. The filename `governor-alpha.json` is retained for URL compatibility; its documented target is **Bravo**, not every Alpha/Bravo deployment.
- **Oracle:** `price-oracle.json` is the read interface for Mainnet's `TGnYnSn4G9PgWFj7QQemh4YMZKp3fkympJ` entrypoint. `assetPrices`, `anchors`, `poster`, `getPrice`, and `setPrice` belong to its `v1PriceOracle()` backend, `TMiNCmvD3zdsv6mk7niBU6NPBzVNjYMQTV`; those verified methods are provided separately in `price-oracle-impl.json`. Do not send a backend-only call to the proxy. `setPrice` is a restricted state-changing operation, not a public read.
- **sTRX:** `strx.json` remains **function-only** and does not contain `Deposit`, `Withdraw`, or `Claim` event definitions. A complete matching deployment ABI was not obtained; use a verified build artifact for the current implementation before event decoding. Do not guess field types or which fields are `indexed` from a prose event name.
- **jTRX / WJST:** the native-TRX repayment and WJST vote-unlocking interfaces were checked against their Mainnet node ABIs. Other files remain subsets; entries absent from them are unsupported by that download.

## Catalog

| ABI | Contract | Use for |
|-----|----------|---------|
| [`jtoken.json`](jtoken.json) | jTRC20 (Supply & Borrow Market) | Selected token/lending functions only; no events. Use the native-TRX variants below where applicable. |
| [`jtrx-mint.json`](jtrx-mint.json) | jTRX `mint` (TRX-specific) | Payable `mint` entry point for the native-TRX market (TRX is sent as `callValue`, no `approve`). |
| [`jtrx-repay.json`](jtrx-repay.json) | Mainnet jTRX repayment | Payable `repayBorrow(uint256)` and `repayBorrowBehalf(address)`; payment uses `callValue`. |
| [`comptroller.json`](comptroller.json) | Comptroller | `checkMembership`, `enterMarkets`, `collateralFactorMantissa`, `closeFactorMantissa`, `claimReward`, guardian pause flags. |
| [`interest-rate-model.json`](interest-rate-model.json) | Interest Rate Model | `getBorrowRate`, `getSupplyRate`, `baseRatePerBlock`, `multiplierPerBlock`, `jumpMultiplierPerBlock`. |
| [`price-oracle.json`](price-oracle.json) | Price Oracle | `getUnderlyingPrice(jToken)` for collateral and borrow valuation. |
| [`price-oracle-impl.json`](price-oracle-impl.json) | Mainnet Oracle backend | `assetPrices`, `anchors`, `poster`, `getPrice`, restricted `setPrice`, and `PricePosted`. Not the proxy interface. |
| [`governor-alpha.json`](governor-alpha.json) | Mainnet GovernorBravo (legacy filename) | Selected proposal lifecycle and voting methods, `castVoteBySig`, tuple `getReceipt`, and selected proposal/vote events. |
| [`poly.json`](poly.json) | JST voting | `castVote`, `getVoteInfo`, `totalVote`, `surplusVotes`, `jstBalance` (JST-weighted voting helper). |
| [`strx.json`](strx.json) | sTRX (Staked TRX) | Selected staking/balance functions only; **no events**. |
| [`wjst.json`](wjst.json) | Mainnet WJST | Wrapping, available/locked votes, `withdrawVotes`, and selected wrap/vote-lock events. |
| [`trc20.json`](trc20.json) | TRC20 (generic) | `approve`, `allowance`, `balanceOf`, `decimals`, `transfer` for any underlying TRC20 asset. |
| [`energy-market.json`](energy-market.json) | Energy Rental market | `getRentInfo`, rental / stable rates, `feeRatio`, order accounting. |
| [`energy-rate-model.json`](energy-rate-model.json) | Energy Rental rate model | `getRentalRate`, `totalDelegated`, `totalFrozen`. |

## Decoding events

First confirm that the ABI contains the desired `type: "event"` entry and matches the deployed address, implementation, network, and historical block being decoded. If it does not, obtain the corresponding verified build artifact rather than inventing a signature. Only then derive `topic0` from the exact name and input types; `indexed` flags are also necessary to decode topics and data correctly. See [APIs §8 — Event-stream and indexing options](../apis.md#8-event-stream-and-indexing-options).

## For AI agents

- Use these ABIs together with addresses from [`contracts.json`](../contracts.json); never hard-code addresses from prose.
- Respect precision rules: jTokens always use **8** decimals; each underlying TRC20 uses its own `decimals`; mantissa-scaled fields (`exchangeRate`, `borrowIndex`, rates) are scaled by `1e18`. See [APIs §1.3–1.4](../apis.md#13-numeric-formats).
- For wallet-aware contract writes, prefer the [MCP server tools](../../ai_support/mcp_server.md) over raw ABI calls so that side-effect annotations and HITL confirmation apply.
