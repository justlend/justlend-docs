---
title: Common Pitfalls (Developer Reference)
description: The 10 most common foot-guns when integrating with JustLend DAO on TRON — USDT-style approve race, enterMarkets requirement, mint() overload between jTRX and jTRC20, redeem vs redeemUnderlying, jToken decimals mismatch, liquidateBorrow close factor, uint256(-1) magic, TRX gas model, oracle-staleness behavior, and legacy market caveats.
---

# Common Pitfalls

!!! info "About this page"
    **Protocol:** JustLend DAO (Compound V2 fork on TRON) · **Network:** TRON Mainnet (same patterns apply on Nile testnet) · **Scope:** the gotchas that bite even when the [contract reference](supply_and_borrow_market/sbm.md), [APIs](apis.md), and [glossary](../resources/glossary.md) are all open. Each entry is a one-liner symptom → root cause → safe pattern. · **TronWeb convention:** examples use TronWeb 5.x direct style — `contract.method(args).call()` for reads, `contract.method(args).send()` for writes. Set the sender once with `tronWeb.setAddress(address)` or by constructing TronWeb with `privateKey` / `headers`; do not pass `{ from: ... }` to `.send()`. Solidity / Web3.js patterns translate directly with the obvious renames. · **Companion pages:** [Glossary](../resources/glossary.md), [SBM reference](supply_and_borrow_market/sbm.md), [Comptroller reference](supply_and_borrow_market/comptroller.md), [Deployed Contracts](deployed_contracts.md).

## TL;DR for AI agents

| # | Symptom | Pitfall |
|---|---|---|
| 1 | `approve()` reverts mid-flow | USDT-style TRC20 needs `approve(0)` before `approve(N)`. |
| 2 | `borrow()` reverts with `COMPTROLLER_REJECTION` despite plenty of collateral | Forgot `enterMarkets()` — supplied assets do not count as collateral until you opt in. |
| 3 | `mint()` reverts with "wrong number of arguments" | jTRX uses `mint() payable`; jTRC20 uses `mint(uint)`. Different signatures. |
| 4 | `redeem()` returns less than expected | You called `redeem(amount)` thinking it was underlying — `redeem()` takes **jToken units** (8 decimals). Use `redeemUnderlying()` for underlying-denominated. |
| 5 | Off-by-10⁰ to 10¹² errors | jToken is 8 decimals; underlying is its own decimals; you mixed them. |
| 6 | `liquidateBorrow()` reverts with `LIQUIDATE_CLOSE_AMOUNT_IS_UINT_MAX` or too-large | Close factor caps `repayAmount` at **50%** of the borrower's debt for that asset in a single call. |
| 7 | "Full repay" leaves dust | Pass `repayBorrow(uint256(-1))` — i.e. `2^256 - 1` — as the amount sentinel, not your locally-computed balance. |
| 8 | Transaction reverts with "out of energy" despite low gas | TRON's resource model is energy + bandwidth, not gas. Rent energy or stake TRX first. |
| 9 | Oracle price is stale or zero | `Poster`-relayed Chainlink feed; on-chain freshness is not guaranteed. See [Price Oracle](supply_and_borrow_market/price_oracle.md). |
| 10 | New deposit went to a legacy market | `(legacy)`-tagged markets accept deposits at the contract level but are governance-frozen for new business. Filter `status == "active"` in [`contracts.json`](contracts.json). |

---

## 1. USDT-style `approve()` race condition

**Symptom.** Your second call to `approve(jUSDT, N)` reverts. Your `mint(N)` then fails to pull funds.

**Root cause.** Some TRC20s — notably **TRON USDT** (`TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t`) — reject `approve(spender, newAmount)` when the current allowance is non-zero. This is non-standard but historical and not going to change. JustLend markets affected today: `jUSDT`, `jUSDCOLD`, `jTUSD`, `jUSDDOLD`, `jBUSDOLD` (and any future USDT-derived underlying).

**Safe pattern.**

```javascript
// Requires tronWeb.defaultAddress.base58 to be set (via setAddress, privateKey,
// or TronLink injection). Throws early if not — silent "no sender" failures
// are the most common source of confusion in TronWeb.
async function safeApprove(token, spender, amount) {
  const owner = tronWeb.defaultAddress.base58;
  if (!owner) throw new Error('tronWeb.defaultAddress not set');

  const current = (await token.allowance(owner, spender).call()).toString();
  if (current !== '0' && current !== String(amount)) {
    await token.approve(spender, 0).send();
  }
  return token.approve(spender, amount).send();
}
```

Standard-compliant TRC20s (USDD, BTC, WBTC, sTRX, …) tolerate non-zero → non-zero, but running the pattern unconditionally costs one extra `approve(0)` only when changing the value — cheap insurance.

---

## 2. `enterMarkets()` is required for collateral to count

**Symptom.** `borrow()` reverts with `COMPTROLLER_REJECTION` even though you supplied plenty of an asset whose `collateralFactorMantissa > 0`.

**Root cause.** Compound V2's design: supplying tokens credits your jToken balance but **does not automatically opt that jToken in as collateral**. You must call `Comptroller.enterMarkets([jTokenAddr])` once per jToken you want counted.

**Safe pattern (pre-borrow check).**

```javascript
// 1. Make sure we're in every market we want as collateral
const user = tronWeb.defaultAddress.base58;
const inMarkets = await comptroller.getAssetsIn(user).call();
const need = [jUSDT, jTRX].filter(jt => !inMarkets.includes(jt));
if (need.length > 0) {
  await comptroller.enterMarkets(need).send();
}
// 2. Now borrow
const { error, liquidity, shortfall } =
  await comptroller.getAccountLiquidity(user).call();
if (error.toString() !== '0' || shortfall.toString() !== '0') {
  throw new Error('not enough collateral');
}
await jSUN.borrow(amount).send();
```

`exitMarket(jToken)` is the inverse; it reverts if exiting would put the account below the borrow limit.

---

## 3. `mint()` is overloaded — different signature for jTRX vs jTRC20

**jTRX:**
```solidity
function mint() external payable;   // amount is sent via msg.value
```

**Every other jToken (jTRC20):**
```solidity
function mint(uint mintAmount) external returns (uint);  // requires prior approve()
```

Calling `mint(amount)` on jTRX reverts; calling `mint()` on jUSDT reverts. This bites code that auto-dispatches on the jToken address. Branch on the underlying:

```javascript
if (jTokenSymbol === 'jTRX') {
  await jTRX.mint().send({ callValue: amount });
} else {
  await safeApprove(underlying, jToken.address, amount);
  await jToken.mint(amount).send();
}
```

Same overload pattern applies to `repayBorrow(uint)` vs `repayBorrow() payable` and `liquidateBorrow(...)`.

---

## 4. `redeem()` vs `redeemUnderlying()`

| Function | Argument unit | When to use |
|---|---|---|
| `redeem(redeemTokens)` | **jToken** (always 8 decimals) | "Withdraw a specific number of jTokens." |
| `redeemUnderlying(redeemAmount)` | **underlying** (token's own decimals) | "Withdraw a specific number of underlying tokens." |

The arguments are not interchangeable. `redeem(100e6)` on jUSDT redeems `100e6 / 10⁸ = 0.01` jTokens (a tiny amount). `redeemUnderlying(100e6)` on jUSDT redeems whatever number of jTokens is needed to return `100 USDT` (6-decimal underlying). Pick by intent; verify with [`balanceOfUnderlying(user)`](supply_and_borrow_market/sbm.md#underlying-balance) before sending.

---

## 5. jToken (8) ↔ underlying (varies) decimals

**Symptom.** Off-by-10² to 10¹² error in a downstream balance calculation.

**Rule.** Every jToken is 8 decimals. The underlying may be anything from 6 (TRX, USDT, USDC) to 8 (BTC, sTRX) to 18 (USDD, ETH). The exchange rate compensates, but only if you remember which side of the conversion you're on.

```javascript
// jUSDT (jToken 8 dec) ↔ USDT (underlying 6 dec)
// exchange rate is scaled by 1e18 and encodes both the price *and* the decimal diff
const er = BigInt((await jUSDT.exchangeRateCurrent().call()).toString());
const jUSDTBalance = BigInt((await jUSDT.balanceOf(user).call()).toString()); // 8 decimals
const underlyingBalance = jUSDTBalance * er / 10n**18n;                       // 6 decimals
```

The `balanceOfUnderlying(account)` helper does this conversion for you and is the recommended path.

---

## 6. `liquidateBorrow()` close factor (50%)

**Symptom.** Liquidation reverts with `LIQUIDATE_CLOSE_AMOUNT_TOO_LARGE` or similar.

**Rule.** In a single `liquidateBorrow()` call, you may repay **at most `closeFactorMantissa / 1e18 = 50%`** of the borrower's outstanding debt **on that specific borrowed asset**. To fully liquidate, call repeatedly.

```javascript
const debt = BigInt((await jUSDT.borrowBalanceCurrent(borrower).call()).toString());
const closeFactor = BigInt(
  (await comptroller.closeFactorMantissa().call()).toString()
);  // 5e17 = 0.5 = 50%
const maxRepay = debt * closeFactor / 10n**18n;
await jUSDT.liquidateBorrow(borrower, maxRepay.toString(), jCollateral).send();
```

The liquidator receives `repayAmount × liquidationIncentiveMantissa / 1e18` worth of `jCollateral` — for JustLend, `1.08` → 8% bonus over the debt value.

---

## 7. `uint256(-1)` for "repay full balance"

**Symptom.** `repayBorrow(balance)` leaves a tiny residual that keeps the position open.

**Root cause.** Between when you read `borrowBalanceCurrent(account)` off-chain and when the transaction lands on-chain, more interest accrues. Your repay amount is now slightly short.

**Magic sentinel.** Pass `uint256(-1)` — i.e. `2n ** 256n - 1n`, all-ones — as the amount. The contract recognizes this as "repay everything" and uses the freshly-accrued balance internally.

```javascript
const MAX_UINT = 2n ** 256n - 1n;
await jUSDT.repayBorrow(MAX_UINT.toString()).send();
```

Same sentinel works for `repayBorrowBehalf(borrower, MAX_UINT)`. Make sure your `approve()` allowance is at least equal to the current debt (or use `MAX_UINT` for the approval too — but mind pitfall #1 for USDT-style underlyings).

---

## 8. TRON resource model — not Ethereum gas

**Symptom.** "out of energy" revert despite the TRX balance looking fine.

**Difference.** TRON transactions consume **energy** (for contract calls) and **bandwidth** (for byte size), not gas. Account energy/bandwidth replenish daily from staked TRX (TRON Power) or can be rented per-call via [JustLend Energy Rental](energy_rental.md). A `mint` / `borrow` on a jToken typically consumes ~60k–130k energy depending on cold/warm storage and oracle freshness.

**Pre-flight estimator (recommended).** Use the [MCP server's `estimate_lending_energy` tool](../ai_support/mcp_server.md) or query the rental dashboard's `energyStakePerTrx` and convert: needed_energy / energyStakePerTrx = TRX-to-rent. For one-off transactions, the dApp UI handles energy automatically; for programmatic callers, rent in the same transaction batch or pre-stake TRX once.

---

## 9. Oracle freshness is not enforced on-chain

**Symptom.** `getUnderlyingPrice(jToken)` returns a value stale by minutes during a fast market move; liquidations momentarily look healthy when off-chain prices say they're not (or vice versa).

**Root cause.** JustLend's `PriceOracle` is updated by a `Poster` role that relays Chainlink prices on-chain. There is no per-call "must be fresher than X seconds" check inside `getUnderlyingPrice`. The poster has its own update cadence (typically tight, but not contractually bounded).

**Mitigation for integrators.**

- For monitoring / dashboards: cross-check the on-chain oracle against Chainlink's off-chain feed before alerting.
- For liquidation bots: do not assume the oracle moves in lockstep with CEX prices during volatile minutes. Add a fairness window before firing.
- For builders of dependent protocols: consider a TWAP read or a freshness-required wrapper before quoting prices into your own pricing logic.

See [Price Oracle reference](supply_and_borrow_market/price_oracle.md).

---

## 10. Legacy markets

**Symptom.** A user "supplies" to `jUSDCOLD` and is surprised it doesn't show on the dApp.

**Status field.** Each jToken in [`contracts.json`](contracts.json) carries `status: "active" | "legacy"`. Current `legacy` markets: `jUSDCOLD`, `jUSDDOLD`, `jBUSDOLD`, `jSUNOLD`, `jUSDJ`, `jWBTT`. These are **closed to new supply and borrow at the dApp / policy layer**, but the contracts are still live on-chain — a direct `mint()` may technically succeed.

**Filter at the policy layer**, not the contract layer:

```javascript
// AI agent / integration code
const markets = (await fetch('/lend/jtoken').then(r => r.json())).data.tokenList;
const active = markets.filter(m =>
  contractsJson.networks.mainnet.jtokens[m.symbol]?.status === 'active'
);
```

Existing positions on legacy markets remain operable — borrowers can `repayBorrow`, suppliers can `redeem` — but **do not direct new deposits to legacy markets** without explicit user consent. There is currently no announced sunset date for the legacy contracts themselves; they remain queryable indefinitely.

---

## Where to look next

- [SBM contract reference](supply_and_borrow_market/sbm.md) — full function signatures + TronWeb examples.
- [APIs §1](apis.md#1-conventions) — envelope, units, error codes for the public HTTP API.
- [Glossary](../resources/glossary.md) — precise term definitions referenced from this page.
- [`/llms-full.txt`](../llms-full.txt) — single-file snapshot for one-shot LLM ingestion.
