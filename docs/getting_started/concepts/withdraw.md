---
title: Withdraw on JustLend DAO
description: How users redeem supplied assets on JustLend — by jToken amount (`redeem`) or by exact underlying amount (`redeemUnderlying`), subject to market liquidity and collateral constraints.
---

# Withdraw

!!! info "About this page"
    * **Protocol:** JustLend DAO (Compound V2 fork on TRON) 
    * **Network:** TRON Mainnet 
    * **Scope:** user-facing withdraw / redeem flow — liquidity and collateral preconditions, two redeem variants (by jToken units vs. by exact underlying). 
    * **Units:** jToken amounts use **8 decimals** regardless of underlying; underlying amounts use the token's own decimals. 
    * **Related contracts:** [SBM `redeem` / `redeemUnderlying`](../../developers/supply_and_borrow_market/sbm.md) and the [Comptroller liquidity check](../../developers/supply_and_borrow_market/comptroller.md#get-account-liquidity).


JustLend DAO empowers users to manage their assets effectively by enabling the withdrawal of supplied tokens. Suppliers can withdraw their tokens as long as there is sufficient liquidity in the reserve. The withdrawal amount is determined by the availability of underlying assets and the user’s ability to maintain a sufficient collateral ratio for any active borrow positions.

When withdrawing with an active borrow position, it’s essential to carefully manage your collateralisation ratio to avoid liquidation. Reducing collateral will decrease the health status and increasing the risk of liquidation.

#### To stay safe:
* **Monitor Your Risk Value:** Ensure your risk value remains health even after the withdrawal;
* **Stay Below the Liquidation Threshold:** Check that your account maintains sufficient collateral to avoid crossing the liquidation parameters;
* **Plan Withdrawals Carefully:** Assess the impact of each withdrawal on your overall borrow position to prevent unintentional liquidation risks.


### **How Do I Withdraw Assets**

* Connect your Web3 wallet on TronLink or other supported wallet app to the JustLend DAO ([https://justlend.org](https://justlend.org)).
* To Withdraw Asset on SBM V1:
    * Navigate to **“SBM V1”**, choose the asset you wish to withdraw, then click **「Withdraw」** under supplied assets.
    * Enter the amount you want to withdraw, then click **「Withdraw」** and confirm the transaction.
* To Withdraw Asset on SBM V2:
    * Navigate to **“SBM V2”**, select the withdrawal asset under **All Supply Vaults**, then click **「Details」**.
    * Choose **Withdraw**, enter the withdrawal amount, then click **「Withdraw」**.


### Developer reference

- Contract function (by jToken units): [`redeem(redeemTokens)`](../../developers/supply_and_borrow_market/sbm.md#redeem) — burns the specified jToken amount and returns the equivalent underlying.
- Contract function (by exact underlying amount): [`redeemUnderlying(redeemAmount)`](../../developers/supply_and_borrow_market/sbm.md#redeemunderlying) — burns enough jTokens to return exactly `redeemAmount` of underlying.
- Both revert if liquidity falls below the borrow position's collateral requirement; check [`getAccountLiquidity(account)`](../../developers/supply_and_borrow_market/comptroller.md#get-account-liquidity) before withdrawing collateral.
- Live runnable example: [Redeem by jToken vs underlying — TronWeb](../../developers/supply_and_borrow_market/sbm.md#examples-tronweb).
