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
