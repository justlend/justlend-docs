---
title: Supply on JustLend DAO
description: How users supply TRX or TRC20 assets to JustLend money markets to earn interest, receive jTokens, and use the supplied assets as collateral.
---

# Supply

!!! info "About this page"
    **Protocol:** JustLend DAO (Compound V2 fork on TRON) · **Network:** TRON Mainnet · **Scope:** user-facing supply flow — what supplying does, jToken receipts, how interest accrues, and which contract function backs it. · **Units:** supply / underlying amounts use each token's own decimals (TRX = 6, USDT = 6, USDD = 18, BTC = 8, ETH = 18); jToken balances always use **8 decimals**; APY values are annualized decimals (multiply by 100 for %). · **Related contracts:** `CErc20Delegator` jTokens (`mint`, `redeem`, `redeemUnderlying`, see [SBM](../../developers/supply_and_borrow_market/sbm.md)).

Supplying tokens to the JustLend DAO allows users to earn interest on their digital assets while simultaneously using them as collateral for borrowing. When users supply tokens, these assets are deposited into the JustLend DAO liquidity pool, a system of smart contracts designed to facilitate secure, over-collateralized borrowing.

In return, users receive jTokens, TRC-20 tokens representing their supplied assets. jTokens can be redeemed at any time for the underlying assets. As interest accrues, the exchange rate of jTokens relative to the underlying assets increases over time, reflecting the earned interest. This ensures that users benefit from a seamless and dynamic interest compounding mechanism while maintaining liquidity through redeemable jTokens.

### **How It Works**

**Interest Accrual:** Supplied tokens automatically earn interest based on the current market supply rate. Interest is dynamically accrued as the balance of supplied tokens grows, ensuring that users benefit from up-to-date rates.

**Determining Interest Rates:** Interest rates for suppliers are primarily influenced by the borrow utilization rate, which reflects the proportion of assets borrowed relative to the total pool supply. Governance parameters, such as the collateral factor and interest rates, can also be adjusted through community decisions.

**Dynamic Rate Updates:** As tokens are supplied, borrowed, repaid, or withdrawn from the liquidity pool, interest rates are updated in real time. These adjustments are guided by on-chain data, including token balances, oracle-determined prices, and the borrow utilization ratio.

### **How Do I Supply Assets**
Supplying can be done with a user interface [JustLend SBM](https://app.justlend.org/homeNew?lang=en-US). Before we walk through the steps of a supplying sequence, let’s cover some key parameters:

* **Supply APY:** the annual rewards from the jTokens users receive by supplying assets, influenced by the borrow utilization rate and fluctuating over time.
* **Total Supply:** the total supply in the market. As the total supply changes, the Supply APY will also change accordingly.
* **Suppliers:** the number of users participating in the supply market.

#### Supply Assets
1. Connect your Web3 wallet on TronLink or other supported wallet app to the JustLend DAO ([https://justlend.org](https://justlend.org)).
2. Navigate to the "SBM" and choose the asset you want to supply. For example, if you want to supply TRX, click 「Supply」 on the TRX market.
3. Specify the amount you want to supply. The selected assets are transferred directly from your wallet to JustLend DAO protocol, earning interest immediately. This interest will be automatically added to your Supply Balance.

### Developer reference

- Contract function: [`mint()` on `CToken.sol`](../../developers/supply_and_borrow_market/sbm.md#mint) — `payable` for jTRX, takes a `mintAmount` for jTRC20 markets.
- Required prerequisite for TRC20 supply: call `approve()` on the underlying TRC20 contract first (granting the jToken delegator allowance).
- Live runnable example: [Supply USDT — TronWeb](../../developers/supply_and_borrow_market/sbm.md#examples-tronweb).
- Exchange rate evolution: [`exchangeRateCurrent()`](../../developers/supply_and_borrow_market/sbm.md#exchangerate) — scaled by `1e18`, increases over time as interest accrues.
- Per-block supply rate: [`supplyRatePerBlock()`](../../developers/supply_and_borrow_market/sbm.md#supply-rate).
- Underlying balance lookup: [`balanceOfUnderlying(owner)`](../../developers/supply_and_borrow_market/sbm.md#underlying-balance).
