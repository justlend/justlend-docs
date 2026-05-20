JustLend DAO empowers users to manage their assets effectively by enabling the withdrawal of supplied tokens. Suppliers can withdraw their tokens as long as there is sufficient liquidity in the reserve. The withdrawal amount is determined by the availability of underlying assets and the user’s ability to maintain a sufficient collateral ratio for any active borrow positions.

When withdrawing with an active borrow position, it’s essential to carefully manage your collateralisation ratio to avoid liquidation. Reducing collateral will decrease the health status and increasing the risk of liquidation.

#### To stay safe:
* **Monitor Your Risk Value:** Ensure your risk value remains health even after the withdrawal;
* **Stay Below the Liquidation Threshold:** Check that your account maintains sufficient collateral to avoid crossing the liquidation parameters;
* **Plan Withdrawals Carefully:** Assess the impact of each withdrawal on your overall borrow position to prevent unintentional liquidation risks.

### **How Do I Withdraw Assets**
1. Connect your Web3 wallet on TronLink or other supported wallet app to the JustLend DAO ([https://justlend.org](https://justlend.org)).
2. Navigate to the "SBM" and choose the supplied asset you want to withdraw, click 「Withdraw」.
3. Specify the amount you want to withdraw and confirm the transaction.

### Developer reference

- Contract function (by jToken units): [`redeem(redeemTokens)`](../../developers/supply_and_borrow_market/sbm.md#redeem) — burns the specified jToken amount and returns the equivalent underlying.
- Contract function (by exact underlying amount): [`redeemUnderlying(redeemAmount)`](../../developers/supply_and_borrow_market/sbm.md#redeemunderlying) — burns enough jTokens to return exactly `redeemAmount` of underlying.
- Both revert if liquidity falls below the borrow position's collateral requirement; check [`getAccountLiquidity(account)`](../../developers/supply_and_borrow_market/comptroller.md#get-account-liquidity) before withdrawing collateral.
- Live runnable example: [Redeem by jToken vs underlying — TronWeb](../../developers/supply_and_borrow_market/sbm.md#examples-tronweb).
