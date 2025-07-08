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

### Liquidation Tool

Liquidation will be triggered when the risk value of your positions hits 100. The liquidator will settle the debt (in the borrowed token), take away the supplied asset (in the corresponding jToken), and earn a liquidation reward equal to 8% of the repaid debt value. It should be noted that each liquidation can only cover the debt of one token.

As a borrower, please keep a close eye on your risk value to prevent liquidation. Once liquidation occurs, you will find a record of your jTokens being transferred out of your wallet.

**Note:** Before you proceed to use the liquidation tool, please be advised that you must first agree to the terms outlined in the [Liquidation Tool Disclaimer](https://docs.justlend.org/resources/risk-warning). This disclaimer is designed to inform you of the risks, responsibilities, and conditions associated with the use of liquidation tool.
By proceeding to use the liquidation tool, you confirm that you have read, understood, and accept the terms of the disclaimer. If you do not agree with any part of the disclaimer, you are not permitted to utilize liquidation tool and discontinue use immediately.

<br>

## **Risks**
The JustLend  DAO Protocol provides decentralized and efficient access to liquidity, empowering users across the TRON ecosystem. However, as with any decentralized finance (DeFi) protocol, there are inherent risks involved. To address these, JustLend has implemented robust risk management measures, ensuring user confidence and protocol resilience. Below, we outline the key risks and the steps taken to mitigate them.

### Smart Contract Risk
Smart contracts are critical to the functioning of the JustLend DAO Protocol, but they can sometimes contain bugs or vulnerabilities in their code, which may compromise the protocol’s security or its reserve tokens. These vulnerabilities could potentially be exploited by malicious actors, affecting the integrity of transactions and liquidity.

#### Mitigation Measures:
* **Public Code Audits:** JustLend DAO's smart contract code is publicly available for external audits. It has undergone multiple professional third-party audits by recognized experts to identify and address any vulnerabilities;
* **Community Review:** Any proposed changes to the protocol are thoroughly reviewed and approved by the JustLend DAO community before implementation, ensuring collective oversight;
* **Bug Bounty Program:** To further reduce the risk of undiscovered vulnerabilities, JustLend DAO runs an ongoing bug bounty program. This incentivizes external developers to identify and report potential issues, allowing them to be fixed before they can cause harm.

### Oracle Risk
JustLend DAO relies on third-party oracles to provide essential data, such as price feeds and redemption ratios for liquid staking tokens. While oracles are vital to the protocol, their reliance introduces the risk of incorrect data being provided if an oracle fails or is compromised. This could lead to inaccurate valuations and potentially harmful actions within the protocol, such as incorrect collateral liquidation or improper lending terms.

#### Mitigation Measures:
* **Decentralized Oracles:** To minimize the risks associated with centralization, JustLend DAO utilizes decentralized oracles like WinkLink, which provide tamper-resistant data feeds. This ensures greater reliability and security, as the data is less susceptible to manipulation or errors from a single source;
* **Community Review:** These decentralized oracles are also equipped with additional security measures that further protect the integrity of the data, reducing the likelihood of inaccurate or malicious inputs.

### Collateral Risk
The assets used as collateral within the JustLend DAO Protocol are subject to market fluctuations. A sharp decline in the value or liquidity of collateral could lead to under-collateralization or even bad debt, which poses a risk to both lenders and the platform as a whole. Without proper safeguards, this could lead to liquidations that do not cover the full value of outstanding loans, resulting in losses for stakeholders.

#### Mitigation Measures:
* **Risk Service Providers:** JustLend DAO partners with reputable risk service providers that continuously monitor the performance of collateral and assess the stability of the market. These services help detect potential risks early and ensure that the collateral remains adequate to cover outstanding loans;
* **Risk Parameters:** JustLend DAO has set key risk parameters, such as, which are borrow limit, designed to protect the protocol from sudden market changes. These parameters help ensure that collateral remains sufficient to secure the borrows, reducing the likelihood of under-collateralization;
* **Governance Oversight:** The JustLend DAO community and governance framework play a crucial role in adjusting these risk parameters based on market conditions. This allows the protocol to remain adaptable and respond to fluctuations in the market, ensuring a balanced and secure lending environment.

### Risk Alert

#### Why can't I receive email notifications?
If you have enabled “Risk Alert” yet still fail to receive email notifications even when the trigger conditions are met, check the following settings:

1. **Mailbox Settings**
   * Junk folder: Check the junk folder in your mailbox. Sometimes, email notifications can be mistakenly classified as junk emails. If you find the target notification in the junk folder, move it to your inbox or add the sender to your “Contacts”.
   * Email filters: Verify if your email service provider has set filters that have blocked or filtered out the email notifications. It is important to make sure the sender’s address is added to your whitelist or allowlist.
2. **Email Sending Issues**
   * Sending delays: Sometimes, email notifications may not come through quickly due to the delay issues. Please be patient and check your inbox again later.
   * Sending failures: If your emails cannot be sent or are rejected, you may also experience difficulty in receiving email notifications. In this case, you can check your outbox about this kind of issue and try again in the JustLend platform.
3. **User Information**
   * Incorrect email address: Make sure you have provided a correct email address in the “Risk Alert” service on JustLend DAO and have verified that your address functions well.

<br>

## **Staked TRX**
Staked TRX is a feature launched by JustLend DAO that enables one-click TRX staking in accordance with Stake 2.0 rules. Once you have staked your TRX, JustLend DAO will take care of the cumbersome procedures, such as Super Representative (SR) voting and reward claiming, and rent out the Energy obtained from TRX staking automatically to generate more yields for you.

The SRs receiving your TRON Power obtained from staking TRX will be decided via voting by sTRX Governance. The whole process will be open, transparent, and fully decentralized.

### Architecture of the sTRX system
![strx architecture](https://raw.githubusercontent.com/hyf1888/JustLend-DAO-Doc/main/images/strx_architecture.png)

* **TRX Holders:** deposit TRX into the TRC484 contract to receive sTRX at the current exchange rate.

* **sTRX Holders:**
  * Convert sTRX back to TRX at the exchange rate to exit the system;
  * Participate in the governance of TRC484, including Super Representative (SR) voting, resource market interest rate adjustments, and other decisions;
  * Use sTRX as a standard TRC20 token to engage with various applications within the TRON ecosystem.

* **Resource Consumers:**
  * Rent resources within TRC484 by staking TRX (TRX deposited in sTRX system cannot be used for this purpose);
  * Return rented resources, pay the rental fees, and reclaim the remaining staked TRX in TRC484.

* **Liquidators:** liquidate overdue resource rental transactions and earn liquidation rewards.

### Staked TRX Yield
The sources of yields form staking TRX is mainly composed of two parts:

* **Voting rewards:** the rewards for voting TRON Power obtained from TRX staking to SRs;
* **Energy rental rewards:** the revenue from Energy Rental on JustLend DAO, distributed to stakers according to the amount and percentage of TRX they have staked.

The staking APY fluctuates with the changes in voting rewards and the Energy rental market. You can check the latest APY anytime in [Staked TRX](https://app.justlend.org/strx?lang=en-US) page.

### Stake and Unstake TRX
* Connect your Web3 wallet on TronLink or other supported wallet app to the JustLend DAO (https://justlend.org).

* **Stake TRX:**
  * Navigate to the "Staked TRX" page, you will see the latest Staked APY;
  * Specify the amount you want to stake, click 「Stake Now」;
  * Cofirm the transaction, then you will receive a proportionate amount of sTRX as the receipt.

* **Unstake TRX:**
  * Unstake on JustLend DAO: Click the 「unstake」 tab, enter the amount of sTRX you want to unstake, and then confirm the transaction;
  * Unstake via a third-party platform: You can initiate transactions on other platforms, such as HTX and SunSwap, to swap your sTRX.

If you unstake your sTRX on JustLend DAO, you need to wait for 14 days before withdrawing the unstaked TRX by clicking 「Withdraw」 on the same page.

<br>

## **Energy Rental**
JustLend DAO integrates the energy rental protocol, which aims to provide users with a more convenient and cheaper way to obtain energy. The energy rental protocol is open to all TRON network users and supports one-to-many renting, enabling users to rent energy not only for themselves but also for others. The user-friendly interface is designed to accommodate users managing multiple orders seamlessly.

When renting energy, you need to specify three key parameters based on your requirements, which are **Rental Amount**, **Rental Duration** and **Receiving Address**.

* **Rental Amount:** the amount of energy you need.
  * The actual energy rented is calculated based on the corresponding proxy TRX amount. Due to market fluctuations, the rented energy amount may experience slight changes during the transaction;
  * **Note:** the energy used will be fully restored after 24 hours and can be used again;
  * If you are not sure about the amount of energy you need, please refer to: One USDT transfer transaction ≈ 120,000 energy. (may fluctuate according to market trading conditions).

* **Rental Duration:** this is the time you need to use the energy.
  * Supports renting by the hour or by the day, with a maximum single rental period of **30** days；
  * Rental duration is calculated at the time of placing the order. Market price fluctuations may result in slight increases or decreases in actual usage time;
  * **Note:** Shorter rental durations are more affected by market price volatility. If the rental duration is less than 3 hours, please be sure to cancel the rent immediately after completing the transaction. This will prevent early liquidation due to price fluctuations and avoid unnecessary losses.

* **Receiving Address:** the address where the rented energy will be allocated.
  * If you rent for yourself, this field is not required. If renting for another address, this field is required.
  * **Note:** Renting for contract addresses is not supported.

### Placing An Order
Once the parameters are set, you can place an order to proceed with the transaction. The rental protocol will require a prepayment, which includes a **deposit** and **rental fee**:

* **Deposit Fee:** calculated as **0.05%** of the TRX required for the rental energy, with a minimum deposit of **40** TRX.
  * If the rent order is returned on time, the deposit is fully refunded. If not returned before expiry, the order may be liquidated, and the deposit will be forfeited to community liquidators as a reward.

* **Rental Fee:** includes **Occupation Fee** (charges based on the rental duration) and **Usage Fee** (charges based on the rental amount):
  * **Occupation Fee:** the energy you use is charged based on the time you use. The longer you use, the more you will be charged.
    * The prepayment includes the occupancy fee for your entire rental time. If you terminate the rent early, the occupancy fee will be refunded in proportion to the occupancy time.

* **Usage Fee:** the cost of your energy usage fee is charged as one day's rental fee based on the amount of energy you rent.
  * Since it takes **24** hours for energy to recover after use, the usage fee is charged based on 1 day.
  * when you return to the energy:
    * If the energy has been fully restored, the usage fee will be fully refunded;
    * If the energy has been used up, **0.5** days of usage fee will be deducted from your account;
    * If part of the energy has been used, your usage fee will be deducted proportionally.

After completing the rental transaction, you can manage your orders via the energy rental interface. Options include returning the rent, extending the rent order, viewing the actual energy received, and checking the remaining rental duration.

We recommend users customize their leasing plans based on their specific needs:
* **For single transactions**, we recommend returning the energy immediately after use. This avoids liquidation and helps save on occupation fees.
* **For users with regular daily transactions**, we suggest opting for a long-term hassle-free rental plan by renting energy for 30 days based on daily energy consumption. With the 24-hour full restoration rule, there is no need to rent excessive amounts of energy.

### Cost Estimation
To provide a clearer understanding of the costs involved in transferring USDT by renting energy versus directly burning TRX, we present the following cost estimates through two examples:

**Scenario 1: Renting 200k Energy for One Day to Transfer USDT**

After renting 200k energy for one day, the USDT transfer is completed, and the rental is terminated immediately. The costs associated with this scenario are based on the prepayment and potential refund formulas previously outlined.

**Scenario 2: Directly Burning TRX to Transfer USDT Without Energy**

In this scenario, TRX is burned directly to facilitate the USDT transfer without renting any energy. The cost incurred here is solely dependent on the amount of TRX burned for the transaction.

**Comparison Insight**
By comparing these two scenarios, it becomes evident that the cost of using rented energy for transaction cost is significantly lower than the cost of directly burning TRX. Additionally, the presence of USDT in the receiving address affects the computational load of the contract, which in turn impacts the overall transaction cost.
