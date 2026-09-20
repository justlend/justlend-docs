---
title: Repay on JustLend DAO
description: How borrowers pay back debt on JustLend — `repayBorrow`, `repayBorrowBehalf`, full-balance repay via `uint256(-1)`, and TRC20 `approve()` pre-flight.
---

# Repay

!!! info "About this page"
    * **Protocol:** JustLend DAO
    * **Network:** TRON Mainnet 
    * **Scope:** user-facing repay flow — `repayBorrow` and `repayBorrowBehalf`, full-balance shortcut via `uint256(-1)`, jTRX payable variant. 
    * **Units:** repay amounts use the underlying token's own decimals. 
    * **Related contracts:** [SBM `repayBorrow` / `repayBorrowBehalf`](../../developers/supply_and_borrow_market/sbm.md).
    

Repaying borrowed tokens is a critical aspect of managing borrow positions on the JustLend DAO Protocol. With flexible repayment options and user-friendly tools, JustLend DAO makes it easy for borrowers to maintain healthy collateralisation ratios and prevent liquidation risks.

Borrowers can repay their loans using the same tokens they borrowed or through jTokens (collateral tokens) of the same underlying asset. Here are some benefits of repayment:

* By reducing the outstanding borrow amount, repayment strengthens the collateralisation ratio, ensuring the position remains adequately collateralised;
* A higher collateralisation ratio minimizes the risk of liquidation by maintaining a safe margin between the collateral value and the borrowed amount;
* Repayment allows borrowers to safely withdraw a portion of their collateral, offering greater flexibility in managing their assets.


### **How Do I Repay Assets**

* Connect your Web3 wallet on TronLink or other supported wallet app to the JustLend DAO ([https://justlend.org](https://justlend.org)).
* To Repay Asset on SBM V1:
    * Navigate to **“SBM V1”**, choose the asset you wish to repay, then click **「Repay」** under borrowed assets;
    * Enter the amount you want to repay, then click **「Repay」** and confirm the transaction.
* To Repay Asset on SBM V2:
    * Navigate to **“SBM V2”**, select the repay asset under **All Borrow Markets**, then click **「Details」**.
    * Choose **Repay/Redeem**, enter the repay amount and redeem amount.
        * You may choose to complete only the Repay operation first. After entering the amount, then click **「Repay」**.
        * You may also complete only the Redeem operation, but ensure that your Risk Level remains within a healthy range, then click **「Redeem」**.
        * Alternatively, you can complete both Repay and Redeem operations simultaneously. In this case, also make sure your Risk Level stays within a healthy range, then click **「Repay & Redeem」**.


### Developer reference

- Contract function: [`repayBorrow(amount)`](../../developers/supply_and_borrow_market/sbm.md#repayborrow) — pass `uint256(-1)` (i.e. `2^256 - 1`) to repay the full outstanding balance.
- Repay on behalf of another account: [`repayBorrowBehalf(borrower, amount)`](../../developers/supply_and_borrow_market/sbm.md#repayborrowbehalf).
- Required prerequisite for TRC20 markets: `approve()` on the underlying for the jToken delegator.
- For jTRX, the call is `payable` — pass the TRX amount via `msg.value`.
- Live runnable example: [Repay USDT — TronWeb](../../developers/supply_and_borrow_market/sbm.md#examples-tronweb).
