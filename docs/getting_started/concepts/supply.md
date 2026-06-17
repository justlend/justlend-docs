---
title: Supply on JustLend DAO
description: How users supply TRX or TRC20 assets to JustLend money markets to earn interest, receive jTokens, and use the supplied assets as collateral.
---

# Supply

!!! info "About this page"
    * **Protocol:** JustLend DAO
    * **Network:** TRON Mainnet
    * **Scope:** user-facing supply flow — what supplying does, jToken receipts, how interest accrues, and which contract function backs it.
    * **Units:** supply / underlying amounts use each token's own decimals (TRX = 6, USDT = 6, USDD = 18, BTC = 8, ETH = 18); [jToken balances always use **8 decimals**]    (../../resources/glossary.md#jtoken-decimals); APY values are annualized decimals (multiply by 100 for %).
    * **Related contracts:** `CErc20Delegator` jTokens (`mint`, `redeem`, `redeemUnderlying`, see [SBM](../../developers/supply_and_borrow_market/sbm.md)).
    * **For developers:** [Common Pitfalls #1 (USDT approve race) and #5 (decimals mismatch)](../../developers/common_pitfalls.md).


Supplying tokens to the JustLend DAO allows users to earn interest on their digital assets while simultaneously using them as collateral for borrowing. When users supply tokens, these assets are deposited into the JustLend DAO liquidity pool, a system of smart contracts designed to facilitate secure, over-collateralized borrowing.

In return, users receive jTokens, TRC-20 tokens representing their supplied assets. jTokens can be redeemed at any time for the underlying assets. As interest accrues, the exchange rate of jTokens relative to the underlying assets increases over time, reflecting the earned interest. This ensures that users benefit from a seamless and dynamic interest compounding mechanism while maintaining liquidity through redeemable jTokens.

### **How It Works**

**Interest Accrual:** Supplied tokens automatically earn interest based on the current market supply rate. Interest is dynamically accrued as the balance of supplied tokens grows, ensuring that users benefit from up-to-date rates.

**Determining Interest Rates:** Interest rates for suppliers are primarily influenced by the borrow utilization rate, which reflects the proportion of assets borrowed relative to the total pool supply. Governance parameters, such as the collateral factor and interest rates, can also be adjusted through community decisions.

**Dynamic Rate Updates:** As tokens are supplied, borrowed, repaid, or withdrawn from the liquidity pool, interest rates are updated in real time. These adjustments are guided by on-chain data, including token balances, oracle-determined prices, and the borrow utilization ratio.

### **How Do I Supply Assets**
Supplying can be done with a user interface [JustLend SBM V1](https://app.justlend.org/homeV1) or [SBM V2](https://app.justlend.org/homeNew?lang=en-US). Before we walk through the steps of a supplying sequence, let’s cover some key parameters:

**SBM V1:**

* `Supply APY:` the annual rewards from the jTokens users receive by supplying assets, which influenced by the borrow utilization rate and fluctuated by the time;
* `Total Supply:` the total supply in the market. As the total supply changes, the Supply APY will also change accordingly;
* `Suppliers:` the amount of users participating in the supply market.

**SBM V2:**

* `Supply APY:` the annualized return earned from supplying assets to the Vault. It is influenced by the market’s borrow utilization rate and may fluctuate over time;
* `Total Supply:` the total amount of assets supplied in the market. As the total supply changes, the Supply APY will adjust accordingly;
* `Collateral Support:` refers to the types of assets supported across the underlying Markets connected to this Vault. While you only deposit a single asset into the Vault, your liquidity may be lent out to borrowers who pledge these supported collateral tokens.


#### Supply Assets

* Connect your Web3 wallet on TronLink or other supported wallet app to the JustLend DAO ([https://justlend.org](https://justlend.org)).
* To Supply Asset on SBM V1：
    * Navigate to **“SBM V1”**, choose the asset you wish to supply, then click **「Supply」** in the corresponding  market.
    * Enter the amount you want to supply and click **「Supply」**.
* To supply Asset on SBM V2:
    * Navigate to **“SBM V2”**, select the asset under **All Supply Vaults**, then click **「Details」**.
    * Choose **Supply**, enter the supply amount, then click **「Supply」**.

After the contract is successfully approved, the assets will be transferred from your wallet to the JustLend DAO protocol. Once they are borrowed by other users, they will begin generating interest. This interest will be automatically added to your Supply Balance.


### Developer reference

- Contract function: [`mint()` on `CToken.sol`](../../developers/supply_and_borrow_market/sbm.md#mint) — `payable` for jTRX, takes a `mintAmount` for jTRC20 markets.
- Required prerequisite for TRC20 supply: call `approve()` on the underlying TRC20 contract first (granting the jToken delegator allowance).
- Live runnable example: [Supply USDT — TronWeb](../../developers/supply_and_borrow_market/sbm.md#examples-tronweb).
- Exchange rate evolution: [`exchangeRateCurrent()`](../../developers/supply_and_borrow_market/sbm.md#exchangerate) — scaled by `1e18`, increases over time as interest accrues.
- Per-block supply rate: [`supplyRatePerBlock()`](../../developers/supply_and_borrow_market/sbm.md#supply-rate).
- Underlying balance lookup: [`balanceOfUnderlying(owner)`](../../developers/supply_and_borrow_market/sbm.md#underlying-balance).
