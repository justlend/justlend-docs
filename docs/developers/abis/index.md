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

The [2026-10-14 verification evidence](../verification_evidence.md) documents the exact proxy getters, node ABI sources, compiler comparison, source-only tuple expansion, and remaining issue coverage. The [machine-readable snapshot](../verification-evidence-20261014.json) records the checked interface entries and request/response words. It is a dated, non-atomic read snapshot, not a guarantee about a future upgrade or historical deployment.

The [machine-readable scope manifest](manifest.json) records the corrections checked on **2026-10-12**:

- **GovernorBravo:** Mainnet proxy `TEqiF5JbhDPD77yjEfnEMncGRZNDt2uogD` returned implementation `TUeNh9BsYK44XePmFAuKZWg2rJuU7bSt5u`. Input types and selected events were taken from that implementation's node ABI. `getReceipt` returns one tuple; its `bool / uint8 / uint96` components were expanded from the pinned official source because the node omits tuple components. This is not a bytecode-reproduced compiler artifact. The filename `governor-alpha.json` is retained for URL compatibility; its documented target is **Bravo**, not every Alpha/Bravo deployment.
- **Oracle:** `price-oracle.json` is the read interface for Mainnet's `TGnYnSn4G9PgWFj7QQemh4YMZKp3fkympJ` entrypoint. `assetPrices`, `anchors`, `poster`, `getPrice`, and `setPrice` belong to its `v1PriceOracle()` backend, `TMiNCmvD3zdsv6mk7niBU6NPBzVNjYMQTV`; those verified methods are provided separately in `price-oracle-impl.json`. Do not send a backend-only call to the proxy. `setPrice` is a restricted state-changing operation, not a public read.
- **sTRX:** `strx.json` includes selected functions (with corrected return types) and all **27 event declarations** from the current Mainnet `STRXG2` implementation, `TUAV6ZSCXtF8KVvDKSeVmAbJEovTBf4HtG`. This includes `Deposit`, `Withdraw`, and `Claim`, with `user` indexed. The functions now include `withdrawExact` and `claim`. This is still a subset of functions and excludes the separate administrative proxy ABI; it is not a guarantee for historical implementations or Nile.
- **Energy Rental:** `energy-market.json` includes `strx`, `totalRent`, `rentClaimed`, restricted `claimRental`, and `RentClaimed` from Mainnet `MarketG1`, `TNoHbPuBQrVanVf9qxUsSvHdB2eDkeDAKD`. `claimRental()` returns the amount transferred to sTRX **in that call**, in sun; `rentClaimed()` is the cumulative read. See [Protocol income collection](../energy_rental.md#protocol-income-collection).
- **jTRX / WJST:** the native-TRX repayment and WJST vote-unlocking interfaces were checked against their Mainnet node ABIs. Other files remain subsets; entries absent from them are unsupported by that download.

The sTRX and rental additions were compiled with [TRON Solidity 0.8.18](https://github.com/tronprotocol/solidity/releases/tag/tv_0.8.18), optimizer enabled with 200 runs. Their creation bytecode matches the current node responses after removing **only** trailing Solidity CBOR metadata and its length; full metadata is **not** identical, and a complete reproducible source bundle is not included here. The manifest records compiler and bytecode hashes. `Deposit`, `Withdraw`, `Claim`, and `RentClaimed` were additionally decoded from successful Mainnet transaction receipts and checked against confirmed TronGrid events; raw-log regression fixtures are stored in `scripts/fixtures/docs-verification/settlement-events.json` in the docs repository. No transaction was submitted for verification.

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
| [`strx.json`](strx.json) | sTRX (Staked TRX) | Selected staking/balance functions plus all 27 current STRXG2 event declarations, including `Deposit`, `Withdraw`, and `Claim`. |
| [`wjst.json`](wjst.json) | Mainnet WJST | Wrapping, available/locked votes, `withdrawVotes`, and selected wrap/vote-lock events. |
| [`trc20.json`](trc20.json) | TRC20 (generic) | `approve`, `allowance`, `balanceOf`, `decimals`, `transfer` for any underlying TRC20 asset. |
| [`energy-market.json`](energy-market.json) | Energy Rental market | Compiler-aligned rental/order reads, tuple `rentals`, three-value `getRentInfo`, bool `rentPaused`, refund returns, settlement reads/writes, and `RentResource` / `ReturnResource` / `Liquidate` / `RentClaimed`. |
| [`energy-rate-model.json`](energy-rate-model.json) | Energy Rental rate model | `getRentalRate`, `totalDelegated`, `totalFrozen`. |

## Decoding events

First confirm that the ABI contains the desired `type: "event"` entry and matches the deployed address, implementation, network, and historical block being decoded. If it does not, obtain the corresponding verified build artifact rather than inventing a signature. Only then derive `topic0` from the exact name and input types; `indexed` flags are also necessary to decode topics and data correctly. See [APIs §8 — Event-stream and indexing options](../apis.md#8-event-stream-and-indexing-options).

## For AI agents

- Use these ABIs together with addresses from [`contracts.json`](../contracts.json); never hard-code addresses from prose.
- Respect precision rules: jTokens always use **8** decimals; each underlying TRC20 uses its own `decimals`; mantissa-scaled fields (`exchangeRate`, `borrowIndex`, rates) are scaled by `1e18`. See [APIs §1.3–1.4](../apis.md#13-numeric-formats).
- For wallet-aware contract writes, prefer the [MCP server tools](../../ai_support/mcp_server.md) over raw ABI calls so that side-effect annotations and HITL confirmation apply.
