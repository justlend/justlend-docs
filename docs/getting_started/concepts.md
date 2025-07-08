## **Supply**
Supplying tokens to the JustLend DAO allows users to earn interest on their digital assets while simultaneously using them as collateral for borrowing. When users supply tokens, these assets are deposited into the JustLend DAO liquidity pool, a system of smart contracts designed to facilitate secure, over-collateralized borrowing.

In return, users receive jTokens, TRC-20 tokens representing their supplied assets. jTokens can be redeemed at any time for the underlying assets. As interest accrues, the exchange rate of jTokens relative to the underlying assets increases over time, reflecting the earned interest. This ensures that users benefit from a seamless and dynamic interest compounding mechanism while maintaining liquidity through redeemable jTokens.

### How It Works

**Interest Accrual:** Supplied tokens automatically earn interest based on the current market supply rate. Interest is dynamically accrued as the balance of supplied tokens grows, ensuring that users benefit from up-to-date rates.

**Determining Interest Rates:** Interest rates for suppliers are primarily influenced by the borrow utilization rate, which reflects the proportion of assets borrowed relative to the total pool supply. Governance parameters, such as the collateral factor and interest rates, can also be adjusted through community decisions.

**Dynamic Rate Updates:** As tokens are supplied, borrowed, repaid, or withdrawn from the liquidity pool, interest rates are updated in real time. These adjustments are guided by on-chain data, including token balances, oracle-determined prices, and the borrow utilization ratio.

### How Do I Supply Assets
Supplying can be done with a user interface [JustLend SBM](https://app.justlend.org/homeNew?lang=en-US). Before we walk through the steps of a supplying sequence, let’s cover some key parameters:

* `Supply APY:` the annual rewards from the jTokens users receive by supplying assets, which influenced by the borrow utilization rate and fluctuated by the time;
* `Total Supply:` the total supply in the market. As the total supply changes, the Supply APY will also change accordingly;
* `Suppliers:` the amount of users participating in the supply market.

#### Supply Assets
1. Connect your Web3 wallet on TronLink or other supported wallet app to the JustLend DAO ([https://justlend.org](https://justlend.org)).
2. Navigate to the "SBM" and choose the asset you want to supply. For example, if you want to supply TRX, click 「Supply」 on the TRX market.
3. Specify the amount you want to supply. The selected assets are transferred directly from your wallet to JustLend DAO protocol, earning interest immediately. This interest will be automatically added to your Supply Balance.

<br>

## **Borrow**

The JustLend DAO offers user an efficient way to access liquidity by using their supplied assets as collateral. This approach unlocks capital without requiring users to sell their holdings, making it a powerful tool for managing financial needs. However, borrowers must remain vigilant about potential risks, especially liquidation.

### How It Works

Borrowing on JustLend DAO is simple and dynamic. Users can leverage their deposited assets to borrow tokens, with interest rates determined by the protocol’s utilization rate—the percentage of supplied liquidity currently borrowed. As borrowing demand increases, utilization rates rise, leading to higher interest rates. This dynamic adjustment ensures a balanced ecosystem that benefits both borrowers and suppliers.

**Dynamic Interest Rates:** Interest rates are influenced by protocol mechanics and community governance, adapting to changes in borrowing activity. This system allows the platform to respond effectively to market conditions.

**Reserve Parameters:** Each reserve in the JustLend DAO Protocol is designed with specific parameters to attract both borrowers and suppliers, ensuring a steady flow of liquidity.

**Liquidation Risk:** Borrowers face liquidation if their risk value over the required threshold. To mitigate this, it’s essential to monitor collateralisation levels and maintain a healthy health factor.

### How Do I Supply Assets
Borrowing can be done with a user interface [JustLend SBM](https://app.justlend.org/homeNew?lang=en-US). Before we walk through the steps of a borrowing sequence, let’s cover some key parameters:

* `Borrow APY:` the cost of borrowing assets in the JustLend DAO Protocol, which can vary based on the overall utilization of the liquidity pool；
* `Total Borrow:` the total borrow amount in the market. As the total borrow changes, the borrow APY will also change accordingly;
* `Borrowers:` the amount of users participating in the borrow market;
* `Collateral Factor:` the amount of asset you can borrow compared to the value of jTokens you own. It determines the maximum amount you can borrow based on your supplied asset in this market;
* `Borrow limit:` the minimum amount required to participate in the borrowing market;
* `Liquidation:` a borrowing account becomes insolvent when the borrow balance exceeds the amount allowed by the collateral factor. Other users can repay a portion of its outstanding borrow in exchange for a portion of its collateral, with a liquidation incentive.

#### Supply Assets
1. Connect your Web3 wallet on TronLink or other supported wallet app to the JustLend DAO ([https://justlend.org](https://justlend.org)).
2. Navigate to the "SBM" and choose the asset you want to borrow from the supported assets listed on the markets. For example, if you want to borrow TRX, click 「Borrow」 on the TRX market.
3. Specify the amount you want to borrow and confirm the transaction.

<br>

## **Withdraw**
JustLend DAO empowers users to manage their assets effectively by enabling the withdrawal of supplied tokens. Suppliers can withdraw their tokens as long as there is sufficient liquidity in the reserve. The withdrawal amount is determined by the availability of underlying assets and the user’s ability to maintain a sufficient collateral ratio for any active borrow positions.

When withdrawing with an active borrow position, it’s essential to carefully manage your collateralisation ratio to avoid liquidation. Reducing collateral will decrease the health status and increasing the risk of liquidation.

#### To stay safe:
* **Monitor Your Risk Value:** Ensure your risk value remains health even after the withdrawal;
* **Stay Below the Liquidation Threshold:** Check that your account maintains sufficient collateral to avoid crossing the liquidation parameters;
* **Plan Withdrawals Carefully:** Assess the impact of each withdrawal on your overall borrow position to prevent unintentional liquidation risks.

#### Withdraw Assets:
1. Connect your Web3 wallet on TronLink or other supported wallet app to the JustLend DAO ([https://justlend.org](https://justlend.org)).
2. Navigate to the "SBM" and choose the supplied asset you want to withdraw, click 「Withdraw」.
3. Specify the amount you want to withdraw and confirm the transaction.

<br>

## **Repay**
Repaying borrowed tokens is a critical aspect of managing borrow positions on the JustLend DAO Protocol. With flexible repayment options and user-friendly tools, JustLend DAO makes it easy for borrowers to maintain healthy collateralisation ratios and prevent liquidation risks.

Borrowers can repay their loans using the same tokens they borrowed or through jTokens (collateral tokens) of the same underlying asset. Here are some benefits of repayment:

* By reducing the outstanding borrow amount, repayment strengthens the collateralisation ratio, ensuring the position remains adequately collateralised;
* A higher collateralisation ratio minimizes the risk of liquidation by maintaining a safe margin between the collateral value and the borrowed amount;
* Repayment allows borrowers to safely withdraw a portion of their collateral, offering greater flexibility in managing their assets.

#### Repay Assets:
1. Connect your Web3 wallet on TronLink or other supported wallet app to the JustLend DAO ([https://justlend.org](https://justlend.org)).
2. Navigate to the "SBM" and choose the borrowed asset you want to withdraw, click 「Repay」.
3. Specify the amount you want to repay and confirm the transaction.

<br>

## **Liquidations**

Liquidation is determined by **Risk Value**, which is a critical metric within the JustLend DAO Protocol that measures the safety of a borrow position. It is calculated as:

**Risk Value = Total Borrow / Borrow Limit * 100**

<div style="text-align: center; font-size: 16px;">
    Risk Value = Total Borrow / Borrow Limit * 100
</div>

* `Total Borrow:` sum of all assets borrowed by the user;
* `Borrow Limit:` ∑ (Asset supplied by the user * Collateral Factor of the asset).

The **Risk Value** measures a borrow position’s stability. The Borrow Limit, set by JustLend DAO Governance for each asset, determines the maximum percentage of value that can be borrowed against the asset. For example, if a user supplies $100 in TRX with an collateral factor 80% and $200 in SUN with an collateral factor 75%. Then, borrows $90 worth of USDD and $50 worth of JST tokens from SBM. we can see:

**Borrow Limit**  =  ∑ (Asset supplied * Collateral Factor) = 100 * 80% + 200 * 75% = 230
**Risk Value**  =  Total Borrow / Borrow Limit * 100 = (90 + 50) / 230 * 100 = 60.87

A risk value above 100 represents a position that is above the liquidation threshold. Regular monitoring is essential, as the risk value fluctuates based on both the value of collateral factor and borrowed assets. To reduce the risk value , users can either supply more collateral or repay part of the borrow position. The risk value is directly tied to collateral value. If the collateral value increases, the risk value  decrease; if it falls, the risk value increases, increasing the risk of liquidation.

| range    | Levels of risk      | Recommendations                                                                                                     |
|----------|---------------------|---------------------------------------------------------------------------------------------------------------------|
| 0-35     | Low Risk            | Healthy portfolio, eligible for loans.                                                                              |
| 35-60    | Medium Risk         | Healthy portfolio overall, eligible for extra loan, but with caution.                                               |
| 60-80    | High Risk           | High Risk Portfolio faces risk of liquidation, and you are advised to add collateral or pay off part of your loans. |
| 80-100   | Extremely High Risk | Collaterals are about to be liquidated, and you are advised to add collateral or pay off part of your loans.                                                                                                                   |

Liquidation occurs when a borrower’s risk value exceeds 100, indicating that their collateral is insufficient to cover the borrowed amount. This can happen due to a decline in collateral value or an increase in the borrowing amount. During a liquidation, a liquidator can repay up to 50% of a borrower's debt for a single asset in one liquidation transaction, and a liquidation fee is applied to the borrower’s collateral. As a permissionless process, any network participant can initiate the liquidation of an eligible position.

### Liquidation Tool

Liquidation will be triggered when the risk value of your positions hits 100. The liquidator will settle the debt (in the borrowed token), take away the supplied asset (in the corresponding jToken), and earn a liquidation reward equal to 8% of the repaid debt value. It should be noted that each liquidation can only cover the debt of one token.

As a borrower, please keep a close eye on your risk value to prevent liquidation. Once liquidation occurs, you will find a record of your jTokens being transferred out of your wallet.

```text
Before you proceed to use the liquidation tool, please be advised that you must first agree to the terms outlined in the <Liquidation Tool Disclaimer>. This disclaimer is designed to inform you of the risks, responsibilities, and conditions associated with the use of liquidation tool.
By proceeding to use the liquidation tool, you confirm that you have read, understood, and accept the terms of the disclaimer. If you do not agree with any part of the disclaimer, you are not permitted to utilize liquidation tool and discontinue use immediately.
```


## **Risks**



## **Staked TRX**


## **Energy Rental**
