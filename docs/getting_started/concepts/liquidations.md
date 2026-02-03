Liquidation is determined by **Risk Value**, which is a critical metric within the JustLend DAO Protocol that measures the safety of a borrow position. It is calculated as:

<div style="text-align: center; font-size: 20px;">
    Risk Value = Total Borrow / Borrow Limit * 100
</div>

* `Total Borrow:` sum of all assets borrowed by the user;
* `Borrow Limit:` ∑ (Asset supplied by the user * Collateral Factor of the asset).

The **Risk Value** measures a borrow position’s stability. The Borrow Limit, set by JustLend DAO Governance for each asset, determines the maximum percentage of value that can be borrowed against the asset. For example, if a user supplies $100 in TRX with an collateral factor 80% and $200 in SUN with an collateral factor 75%. Then, borrows $90 worth of USDD and $50 worth of JST tokens from SBM. we can see:

**Borrow Limit**  =  ∑ (Asset supplied * Collateral Factor) = 100 * 80% + 200 * 75% = 230

**Risk Value**  =  Total Borrow / Borrow Limit * 100 = (90 + 50) / 230 * 100 = 60.87

A risk value above 100 represents a position that is above the liquidation threshold. Regular monitoring is essential, as the risk value fluctuates based on both the value of collateral factor and borrowed assets. To reduce the risk value , users can either supply more collateral or repay part of the borrow position. The risk value is directly tied to collateral value. If the collateral value increases, the risk value  decrease; if it falls, the risk value increases, increasing the risk of liquidation.

| Range  | Levels of risk      | Recommendations                                                                                                     |
|--------|---------------------|---------------------------------------------------------------------------------------------------------------------|
| 0-35   | Low Risk            | Healthy portfolio, eligible for loans.                                                                              |
| 35-60  | Medium Risk         | Healthy portfolio overall, eligible for extra loan, but with caution.                                               |
| 60-80  | High Risk           | High Risk Portfolio faces risk of liquidation, and you are advised to add collateral or pay off part of your loans. |
| 80-100 | Extremely High Risk | Collaterals are about to be liquidated, and you are advised to add collateral or pay off part of your loans.                                                                                                                   |

Liquidation occurs when a borrower’s risk value exceeds 100, indicating that their collateral is insufficient to cover the borrowed amount. This can happen due to a decline in collateral value or an increase in the borrowing amount. During a liquidation, a liquidator can repay up to 50% of a borrower's debt for a single asset in one liquidation transaction, and a liquidation fee is applied to the borrower’s collateral. As a permissionless process, any network participant can initiate the liquidation of an eligible position.

## **Liquidation Tool**

Liquidation will be triggered when the risk value of your positions hits 100. The liquidator will settle the debt (in the borrowed token), take away the supplied asset (in the corresponding jToken), and earn a liquidation reward equal to 8% of the repaid debt value. It should be noted that each liquidation can only cover the debt of one token.

As a borrower, please keep a close eye on your risk value to prevent liquidation. Once liquidation occurs, you will find a record of your jTokens being transferred out of your wallet.

**Note:** Before you proceed to use the liquidation tool, please be advised that you must first agree to the terms outlined in the [Liquidation Tool Disclaimer](https://docs.justlend.org/resources/risk_warning). This disclaimer is designed to inform you of the risks, responsibilities, and conditions associated with the use of liquidation tool.
By proceeding to use the liquidation tool, you confirm that you have read, understood, and accept the terms of the disclaimer. If you do not agree with any part of the disclaimer, you are not permitted to utilize liquidation tool and discontinue use immediately.

## **Liquidation Manual**

This manual provides a step-by-step guide for participating in the liquidation process on the JustLend DAO platform to maintain market stability and earn liquidation rewards. Liquidation can be triggered when a borrower's **Risk Value** exceeds a critical threshold. As a liquidator, you repay the borrower's debt in exchange for their collateral at a discounted rate, effectively earning a **liquidation reward**.

* **Observation Threshold:** Accounts with a **Risk Value > 95** will be listed on the Liquidation page.
* **Liquidation Threshold:** Liquidation becomes executable only when the **Risk Value is ≥ 100**.

### 1. **Preparation**

Before starting, ensure you have met the following requirements:

* **Wallet Connection:**  Connect your compatible wallet (e.g., TronLink) to the JustLend DAO [Liquidation Page](https://app.justlend.org/liquidate?lang=en-US).
* **Token Reserves:** Identify the specific debt token of the target borrower. You must have **sufficient balances** of that specific token in your wallet to cover the repayment.

### 2. **Liquidation Process**

* **Monitor High-Risk Accounts:** Navigate to the [Liquidation Page](https://app.justlend.org/liquidate?lang=en-US) on the JustLend DAO official website. Review the list of accounts with a **Risk Value exceeding 95**. These are   potential candidates for liquidation.

* **Select a Target Account:** Identify an account where the **Risk Value is ≥ 100**. At this stage, the **「Liquidate」** button will become active and clickable.

* **Configure Liquidation Parameters:** Click the **「Liquidate」** button. A pop-up window will appear displaying:

    * The type and amount of collateral you will get.
    * The type and amount of debt to be repaid.
      
    Select the asset you wish to repay and the collateral you wish to claim, then enter the repayment amount.

* **Execute the Transaction:** Confirm the repayment amount. The system will prompt you to sign the transaction via your wallet.
    
    * **Note:** Ensure your wallet has **enough TRX** to cover the energy/bandwidth fees for the smart contract execution.

* **Receive Liquidation Rewards:** Once the transaction is confirmed on-chain, the debt is partially or fully repaid on behalf of the borrower. The corresponding collateral, including the reward, will be automatically transferred to your account.

### 3. **Critical Reminders**

* **First-Come, First-Served:** Liquidation is a competitive process. Multiple liquidators may target the same account simultaneously.
* **Accuracy:** Always double-check the debt token type before the transaction to avoid execution failure due to insufficient specific token balances.
* **Transparency:** All liquidation activities are recorded on the blockchain and can be verified via the JustLend dashboard or TRONSCAN.
