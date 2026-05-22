---
title: Borrow on JustLend DAO
description: How borrowing works on JustLend — over-collateralized loans against supplied assets, dynamic interest rates, collateral factors, and liquidation thresholds on TRON.
---

# Borrow

!!! info "About this page"
    **Protocol:** JustLend DAO (Compound V2 fork on TRON) · **Network:** TRON Mainnet · **Scope:** user-facing borrow flow — required pre-flight ([`enterMarkets`](../../developers/supply_and_borrow_market/comptroller.md)), how rates are computed, what determines [borrow limit](../../resources/glossary.md#borrow-limit), and when a position becomes liquidatable. · **Units:** [Collateral Factor](../../resources/glossary.md#collateral-factor) ∈ [0, 1] decimal (e.g. `0.80` = 80%); Borrow APY is annualized decimal (`0.06` = 6%); borrow amounts use the underlying token's own decimals. · **Related contracts:** [SBM `borrow`](../../developers/supply_and_borrow_market/sbm.md) and [Comptroller `enterMarkets` / `getAccountLiquidity`](../../developers/supply_and_borrow_market/comptroller.md). · **For developers:** see [Common Pitfalls #2 — `enterMarkets()` is required for collateral to count](../../developers/common_pitfalls.md#2-entermarkets-is-required-for-collateral-to-count).

The JustLend DAO offers user an efficient way to access liquidity by using their supplied assets as collateral. This approach unlocks capital without requiring users to sell their holdings, making it a powerful tool for managing financial needs. However, borrowers must remain vigilant about potential risks, especially liquidation.

### **How It Works**

Borrowing on JustLend DAO is simple and dynamic. Users can leverage their deposited assets to borrow tokens, with interest rates determined by the protocol’s utilization rate—the percentage of supplied liquidity currently borrowed. As borrowing demand increases, utilization rates rise, leading to higher interest rates. This dynamic adjustment ensures a balanced ecosystem that benefits both borrowers and suppliers.

**Dynamic Interest Rates:** Interest rates are influenced by protocol mechanics and community governance, adapting to changes in borrowing activity. This system allows the platform to respond effectively to market conditions.

**Reserve Parameters:** Each reserve in the JustLend DAO Protocol is designed with specific parameters to attract both borrowers and suppliers, ensuring a steady flow of liquidity.

**Liquidation Risk:** Borrowers face liquidation if their risk value over the required threshold. To mitigate this, it’s essential to monitor collateralisation levels and maintain a healthy health factor.

### **How Do I Supply Assets**
Borrowing can be done with a user interface [JustLend SBM](https://app.justlend.org/homeNew?lang=en-US). Before we walk through the steps of a borrowing sequence, let’s cover some key parameters:

* **Borrow APY:** the cost of borrowing assets on the JustLend DAO Protocol; varies with overall pool utilization.
* **Total Borrow:** the total borrow amount in the market. As the total borrow changes, the Borrow APY changes accordingly.
* **Borrowers:** the number of users participating in the borrow market.
* **Collateral Factor:** the amount of asset you can borrow relative to the value of jTokens you own. It determines the maximum you can borrow against your supplied asset in this market. Range `[0, 1]` (e.g. `0.80` = 80%).
* **Borrow Limit:** Σ(supplied amount × collateral factor) across the markets the user has entered via `enterMarkets`.
* **Liquidation:** a borrowing account becomes liquidatable when the borrow balance exceeds the amount allowed by the collateral factor. Other users can repay a portion of its outstanding borrow in exchange for a portion of its collateral, with a liquidation incentive.

#### Supply Assets
1. Connect your Web3 wallet on TronLink or other supported wallet app to the JustLend DAO ([https://justlend.org](https://justlend.org)).
2. Navigate to the "SBM" and choose the asset you want to borrow from the supported assets listed on the markets. For example, if you want to borrow TRX, click 「Borrow」 on the TRX market.
3. Specify the amount you want to borrow and confirm the transaction.

### Developer reference

- Contract function: [`borrow(borrowAmount)` on `CToken.sol`](../../developers/supply_and_borrow_market/sbm.md#borrow) — reverts if the account is undercollateralized.
- Required prerequisite: [`enterMarkets(jTokens[])` on Comptroller](../../developers/supply_and_borrow_market/comptroller.md#enter-markets) — supplied assets are **not** counted as collateral until the user enters that market.
- Health check before borrow: [`getAccountLiquidity(account)`](../../developers/supply_and_borrow_market/comptroller.md#get-account-liquidity) returns `(error, liquidity, shortfall)`. Reject if `shortfall > 0`.
- Live runnable example: [Borrow with pre-flight liquidity check — TronWeb](../../developers/supply_and_borrow_market/sbm.md#examples-tronweb).
- Per-block borrow rate: [`borrowRatePerBlock()`](../../developers/supply_and_borrow_market/sbm.md#borrow-rate).
- Current borrow balance: [`borrowBalanceCurrent(account)`](../../developers/supply_and_borrow_market/sbm.md#borrow-balance) — accrues interest before returning.
