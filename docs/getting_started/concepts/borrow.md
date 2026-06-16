---
title: Borrow on JustLend DAO
description: How borrowing works on JustLend — over-collateralized loans against supplied assets, dynamic interest rates, collateral factors, and liquidation thresholds on TRON.
---

# Borrow

!!! info "About this page"
    * **Protocol:** JustLend DAO
    * **Network:** TRON Mainnet
    * **Scope:** user-facing borrow flow — required pre-flight ([`enterMarkets`](../../developers/supply_and_borrow_market/comptroller.md)), how rates are computed, what determines [borrow limit](../../resources/glossary.md#borrow-limit), and when a position becomes liquidatable.
    * **Units:** [Collateral Factor](../../resources/glossary.md#collateral-factor) ∈ [0, 1] decimal (e.g. `0.80` = 80%); Borrow APY is annualized decimal (`0.06` = 6%); borrow amounts use the underlying token's own decimals.
    * **Related contracts:** [SBM `borrow`](../../developers/supply_and_borrow_market/sbm.md) and [Comptroller `enterMarkets` / `getAccountLiquidity`](../../developers/supply_and_borrow_market/comptroller.md).
    * **For developers:** see [Common Pitfalls #2 — `enterMarkets()` is required for collateral to count](../../developers/common_pitfalls.md#2-entermarkets-is-required-for-collateral-to-count).
    

The JustLend DAO offers user an efficient way to access liquidity by using their supplied assets as collateral. This approach unlocks capital without requiring users to sell their holdings, making it a powerful tool for managing financial needs. However, borrowers must remain vigilant about potential risks, especially liquidation.

### **How It Works**

Borrowing on JustLend DAO is simple and dynamic. Users can leverage their deposited assets to borrow tokens, with interest rates determined by the protocol’s utilization rate—the percentage of supplied liquidity currently borrowed. As borrowing demand increases, utilization rates rise, leading to higher interest rates. This dynamic adjustment ensures a balanced ecosystem that benefits both borrowers and suppliers.

**Dynamic Interest Rates:** Interest rates are influenced by protocol mechanics and community governance, adapting to changes in borrowing activity. This system allows the platform to respond effectively to market conditions.

**Reserve Parameters:** Each reserve in the JustLend DAO Protocol is designed with specific parameters to attract both borrowers and suppliers, ensuring a steady flow of liquidity.

**Liquidation Risk:** Borrowers face liquidation if their risk value over the required threshold. To mitigate this, it’s essential to monitor collateralisation levels and maintain a healthy health factor.


### **How Do I Borrow Assets**
Borrowing can be done with a user interface [JustLend SBM](https://app.justlend.org/homeNew?lang=en-US) or SBM V2. Before we walk through the steps of a borrowing sequence, let’s cover some key parameters:

**SBM:**

* `Borrow APY:` the cost of borrowing assets in the JustLend DAO Protocol, which can vary based on the overall utilization of the liquidity pool;
* `Total Borrow:` the total borrow amount in the market. As the total borrow changes, the borrow APY will also change accordingly;
* `Borrowers:` the amount of users participating in the borrow market;
* `Collateral Factor:` the percentage of a supplied asset’s value that can be used as borrowing power within a given market. A higher collateral factor allows users to borrow more against their deposited assets;
* `Borrow limit:` the maximum amount of assets that can be borrowed within a specific market;
* `Liquidation:` a borrowing account becomes insolvent when the borrow balance exceeds the amount allowed by the collateral factor. Other users can repay a portion of its outstanding borrow in exchange for a portion of its collateral, with a liquidation incentive.

**SBM V2:**

* `Borrow Rate:` the interest rate borrowers pay for borrowing a specific asset. It fluctuates based on the market’s borrow utilization rate — as utilization increases, the borrow rate typically rises;
* `Collateral:` the asset a user supplies and designates as collateral to secure their borrowings. If the collateral value falls below the required threshold, liquidation may occur;
* `LLTV:` the maximum borrowing ratio before a position becomes subject to liquidation. For example, an LLTV of 80% means liquidation will occur if the loan value reaches 80% of the collateral value;
* `Liquidity:` the amount of assets currently available in the market for borrowing. High liquidity means more assets are available to borrow; low liquidity may indicate limited borrowing capacity.

#### Borrow Assets

* Connect your Web3 wallet on TronLink or other supported wallet app to the JustLend DAO ([https://justlend.org](https://justlend.org)).
* To borrow Asset on SBM V1:
    * Navigate to **“SBM V1”**, choose the asset you wish to borrow, then click **「Borrow」** in the corresponding  market.
    * Enter the borrowing amount you want to borrow, then click **「Borrow」** and confirm the transaction.
* To borrow Asset on SBM V2:
    * Navigate to **“SBM V2”**, select the market under **All Borrow Markets**, then click **「Details」**.
    * Choose **Borrow/Collateralize**, enter the borrowed amount and collateral amount.
        * You may choose to complete only the Collateralize operation first, but note that collateral does not generate any interest, then click **「Collateralize」**.
        * If you already have sufficient collateral, you may complete only the Borrow operation, but ensure that your **Risk Level** remains within a healthy range, then click **「Borrow」**.
        * You may also complete both the Collateralize and Borrow operations at the same time. In this case as well, make sure your **Risk Level** stays within a healthy range, then click **「Borrow & Collateralize」**.

**Please note** that borrowing assets on the web interface may require up to two signature confirmations in certain cases (an additional signature may be needed when the process involves increasing collateral). Depending on your situation, there may also be signature steps beyond the initial approval. These signature requirements are part of the website’s interaction flow and are not enforced by the underlying smart contract logic.


### Developer reference

- Contract function: [`borrow(borrowAmount)` on `CToken.sol`](../../developers/supply_and_borrow_market/sbm.md#borrow) — reverts if the account is undercollateralized.
- Required prerequisite: [`enterMarkets(jTokens[])` on Comptroller](../../developers/supply_and_borrow_market/comptroller.md#enter-markets) — supplied assets are **not** counted as collateral until the user enters that market.
- Health check before borrow: [`getAccountLiquidity(account)`](../../developers/supply_and_borrow_market/comptroller.md#get-account-liquidity) returns `(error, liquidity, shortfall)`. Reject if `shortfall > 0`.
- Live runnable example: [Borrow with pre-flight liquidity check — TronWeb](../../developers/supply_and_borrow_market/sbm.md#examples-tronweb).
- Per-block borrow rate: [`borrowRatePerBlock()`](../../developers/supply_and_borrow_market/sbm.md#borrow-rate).
- Current borrow balance: [`borrowBalanceCurrent(account)`](../../developers/supply_and_borrow_market/sbm.md#borrow-balance) — accrues interest before returning.
