---
title: Glossary
description: Single-page reference for the precise meaning, units, and on-chain encoding of JustLend DAO and Compound V2 terms — mantissa, kink, utilization, sun, borrow index, collateral / close / reserve factor, exchange rate, liquidation incentive, and more.
---

# Glossary

!!! info "About this page"
    **Protocol:** JustLend DAO (Compound V2 fork on TRON) · **Network:** TRON Mainnet (semantics carry over to Nile testnet) · **Scope:** definitions, units, and on-chain encoding of every protocol-specific term used elsewhere in this documentation. Each entry links to the function that returns or sets the value where applicable.

Terms are grouped by what they describe. Within each group, entries are ordered alphabetically. All scaled values use base-`1e18` unless explicitly noted.

---

## Units of value

### sun

The smallest indivisible unit of TRX on TRON. **1 TRX = 10⁶ sun** (TRX has 6 decimals). All TRX amounts that cross a contract boundary — `msg.value`, `transfer()` amounts, the Price Oracle's denominator — are in sun. The JustLend public HTTP API de-scales TRX amounts back to human-readable TRX (see `*InTrx` fields in [APIs §1.3](../developers/apis.md#13-numeric-formats); see also [§1.4 Rate / APY semantics](../developers/apis.md#14-rate-apy-semantics)).

### mantissa

A fixed-point integer scaled by **`1e18`**. Compound V2 (and JustLend) represents fractional values like rates, factors, and exchange rates as `uint256` mantissas to avoid floating-point. To convert a mantissa back to a human decimal, divide by `1e18`. Examples:

- `collateralFactorMantissa = 800000000000000000` → `0.80` → 80% collateral factor.
- `liquidationIncentiveMantissa = 1080000000000000000` → `1.08` → 8% liquidator reward.
- `exchangeRateMantissa = 200000000000000000000000000` → `2e8` → 1 jToken = 2 × 10⁸ of the underlying's smallest unit (for an 18-decimal underlying paired with 8-decimal jToken, that's 0.2 underlying tokens per jToken).

A "scaled by 1e18" annotation anywhere in this documentation means "this is a mantissa."

### jToken decimals

**jTokens always use 8 decimals**, regardless of the underlying's decimals. So `balanceOf(account)` on a jToken returns a number in units of `10⁻⁸` jToken. `redeem(redeemTokens)` takes its argument in those same 8-decimal units. `redeemUnderlying(redeemAmount)` takes its argument in the underlying's own decimals.

### underlying decimals

Each TRC20 underlying carries its own `decimals()` value. JustLend markets currently span:

| Underlying | decimals |
|---|---|
| TRX (native) | 6 |
| USDT, USDC, TUSD, USDJ, USD1, SUN, BTT, NFT, WIN, JST, HTX | 6 |
| BTC, WBTC, sTRX, wstUSDT | 8 |
| USDD, ETH, ETHB | 18 |
| WBTT | 18 |

For machine consumers, [`/developers/contracts.json` → `networks.*.jtokens.<symbol>.underlying_decimals`](../developers/contracts.json) carries the canonical per-market value.

---

## Interest rate model

### borrowRatePerBlock / supplyRatePerBlock

The per-block interest rate the market currently charges borrowers (and pays suppliers, net of reserves). Mantissa-scaled (`1e18`). To convert to APY:

```text
APY ≈ borrowRatePerBlock / 1e18 × blocksPerYear
blocksPerYear ≈ 10,517,760 on TRON at ~3 s/block (365.25 × 86400 / 3)
```

For precision, **prefer the API's pre-computed `apy` / `supplyRate` / `borrowRate` fields** — they already account for compounding and the current block cadence. See [APIs §1.4](../developers/apis.md#14-rate-apy-semantics).

### borrow index

A monotonically increasing per-market `uint256` that records cumulative interest factor. Stored on the jToken contract. A borrower's outstanding balance at any time is `principalBalance × currentBorrowIndex / borrowIndexAtPrincipalSnapshot`. You normally don't compute this manually — call `borrowBalanceCurrent(account)` and let the contract do it.

### kink

The utilization rate at which the `JumpRateModelV2` switches from the gentle linear segment to the steep linear segment. Mantissa-scaled. Typical value `0.8e18` = 80% utilization. Below the kink, `borrowRate(u) = a₁ × u + b`. Above the kink, `borrowRate(u) = a₁ × kink + a₂ × (u − kink) + b`.

### utilization rate (u)

```text
u = borrows / (cash + borrows − reserves)
```

Ranges from `0` (no borrowing) to `1` (every supplied unit is currently borrowed). Drives both `borrowRatePerBlock` and `supplyRatePerBlock` in real time. See [Interest Rate Model](../developers/supply_and_borrow_market/interest_rate_model.md).

---

## Risk parameters

### borrow cap

A per-market maximum on `totalBorrows`, set by Governance to limit exposure to a single asset. Distinct from **borrow limit** (which is per-account). Borrow caps can be inspected on the Comptroller; when a cap is reached, `borrow()` reverts with a `COMPTROLLER_REJECTION` error.

### borrow limit

The maximum total value (in TRX-equivalent or USD-equivalent) a single account can borrow given its current collateral:

```text
borrowLimit = Σᵢ (suppliedAmountᵢ × oraclePriceᵢ × collateralFactorᵢ)
            over markets i the user has entered via enterMarkets
```

Distinct from **borrow cap**. Computed implicitly inside `getAccountLiquidity(account)` on the Comptroller — `liquidity` is `borrowLimit − totalBorrowValue`.

### close factor

The maximum fraction of a single borrower's debt that a single `liquidateBorrow()` call may repay. Mantissa-scaled. JustLend currently uses `0.5e18` → **50%**. Read via `Comptroller.closeFactorMantissa()`. To fully liquidate an unhealthy account you generally need at least two passes.

### collateral factor

The fraction of a supplied asset's value that the protocol counts toward the user's borrow limit. Mantissa-scaled, in `[0, 0.9e18]`. Set by Governance per market. A `0.80` factor means $100 supplied → $80 toward your borrow limit. Read via `Comptroller.markets(jToken).collateralFactorMantissa`.

### liquidation incentive

The bonus a liquidator receives — paid by seizing extra collateral above the debt being repaid. Mantissa-scaled. JustLend currently uses `1.08e18` → **8% reward** (the liquidator receives 1.08× the repaid debt value in collateral). Read via `Comptroller.liquidationIncentiveMantissa()`.

### reserve factor

The fraction of accrued interest that the protocol retains as reserves rather than passing through to suppliers. Mantissa-scaled, per-market. A `reserveFactor` of `0.1e18` means 10% of borrower interest is held as reserves; 90% flows to suppliers. Read via `<jToken>.reserveFactorMantissa()`. Changed by Governance only.

### Risk Value

JustLend's user-facing single-number health metric. Defined on the dApp and on the [Liquidations page](../getting_started/concepts/liquidations.md):

```text
RiskValue = totalBorrow / borrowLimit × 100
```

A scalar in `[0, ∞)`. Liquidatable when `RiskValue > 100`. Distinct from `getAccountLiquidity(account)` — `Risk Value > 100` ↔ `shortfall > 0`.

---

## Token mechanics

### exchange rate (jToken ↔ underlying)

The current ratio at which `mint`/`redeem` exchange jTokens for the underlying. Mantissa-scaled to `1e18`. Always ≥ initial value (1:1 at deployment, with adjustment for decimal differences), monotonically increases as interest accrues — **the supply yield is captured by exchange-rate appreciation**, not by minting new jTokens.

For an 8-decimal jToken paired with a 6-decimal underlying, the initial exchange rate is `0.02e18` (so 1 jToken at mint = 50 underlying smallest-units = 50 / 10⁶ underlying). Read via `<jToken>.exchangeRateCurrent()` (accrues interest first) or `exchangeRateStored()` (cached).

### exchange rate (sTRX ↔ TRX)

The current ratio at which `deposit`/`withdraw` exchange sTRX for TRX. Mantissa-scaled to `1e18`. Always ≥ 1 (no initial premium), monotonically increases as voting + Energy-Rental rewards accrue. Read via `sTRX.exchangeRate()`.

### redemption ratio

Same concept as **exchange rate** but used colloquially to mean "how much underlying I get back per share." For jTokens it's `exchangeRateMantissa / 1e18`; for sTRX likewise.

---

## Governance

### Vote (1 JST = 1 Vote, after WJST wrap)

Voting power on a JustLend proposal is denominated in **WJST**, which is minted 1:1 by depositing JST into `WJST.deposit()`. Voting weight is the WJST balance at the proposal's voting-snapshot block. Withdrawing WJST back to JST after a proposal closes restores the underlying JST.

### proposal threshold

Minimum JST a single account must hold (via WJST) to call `propose()`. JustLend currently requires **≥ 200,000,000 JST**. Set in `GovernorBravoDelegate`.

### quorum

Minimum For-votes a proposal must receive to be valid, regardless of For-vs-Against ratio. JustLend currently requires **For votes > 600,000,000** AND `For > Against`. See [Governance contract reference](../developers/supply_and_borrow_market/governance.md).

### Timelock

The 48-hour minimum delay between a proposal succeeding (vote period closes with quorum met) and `execute()` becoming callable. Enforced by a separate Timelock contract (`TRWNvb15NmfNKNLhQpxefFz7cNjrYjEw7x`), the only address authorized to call privileged setters on JustLend contracts.

---

## Market status

### active (jToken status)

Open for new supply and borrow. The default state. 17 of 23 jToken markets are currently `active`.

### legacy (jToken status)

**Closed to new supply and borrow.** Existing positions can still be unwound (`repayBorrow`, `redeem`, `redeemUnderlying`). The contract remains queryable indefinitely; addresses do not get reused. 6 of 23 jToken markets are currently `legacy`. The canonical list and per-market `status` field are in [`contracts.json`](../developers/contracts.json) and the [APIs §2 reference table](../developers/apis.md#2-jtoken-address-reference). See also: [Developer common pitfalls — legacy markets](../developers/common_pitfalls.md#10-legacy-markets).

---

## External primitives

### Multicall3

A widely-deployed contract that lets callers bundle many read-only EVM/TVM calls into a single transaction-less RPC request, dramatically reducing round-trip overhead when fetching state across N markets / accounts. On TRON Mainnet, Multicall3 is deployed at **`TX56WKxtja91Dybf2FdN4hZbDLyKVxxhAu`** (verified on-chain — contract name is literally `Multicall3`). The JustLend MCP server uses it to query all jToken markets in a single round trip; see [MCP Server → Account & Balances](../ai_support/mcp_server.md). For your own integrations, the canonical Multicall3 ABI works as-is; no protocol-specific wrapper needed.

---

## Where to look next

- [APIs §1](../developers/apis.md#1-conventions) — concrete API field semantics referencing the same terms.
- [SBM reference](../developers/supply_and_borrow_market/sbm.md) — full function-signature reference for the jToken contract.
- [Common pitfalls](../developers/common_pitfalls.md) — gotchas that bite even when terms are understood correctly.
- [`/llms-full.txt`](../llms-full.txt) — single-file snapshot for one-shot LLM ingestion.
