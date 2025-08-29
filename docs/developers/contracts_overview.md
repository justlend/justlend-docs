# Contracts Overview

JustLend DAO Protocol contracts are divided in these repositories:

* **Supply and Borrow Market:** contains core contracts for JustLend DAO, including logic for supply and borrow market (SBM), interest rate model, governance, price oracle and comptroller.
  * **SBM:** enables supplying of crypto assets as collateral in order to borrow the base asset. Accounts can also earn interest by supplying the base asset to the protocol.
  * **Interest Rate Model:** users with a positive balance of the base asset earn interest, denominated in the base asset, based on a supply rate model.
  * **Price-Oracle:** contains the price oracle contracts we support, along with the logic validation for prices returned by these oracles.
  * **Governance:** contracts used for proposing, voting and executing proposals.
  * **Comptroller:** the risk management layer of the protocol. It determines how much collateral a user is required to maintain, and whether user can be liquidated.
* **Staked TRX:** the contracts utilized for staking TRX to earn high rewards.
* **Energy Rental:** contracts enable users to rent energy anytime with a low price.


## **Core Contracts**
There are 5 categories of core repository contracts:

* JTokens Contract
* Interest Rate Model Contract
* Price Oracle Contract
* Governance Contract
* Comptroller Contract

### JTokens Contract
`JToken:` the contract used to support all assets by JustLend DAO, such as the jTRX, jUSDT, jSUN and jBTC you receive after supplying the corresponding assets.

### Interest Rate Model Contract
`WhitePaperInterestRateModel:` the contract used to set up a straightforward interest rate model, which the borrowing rate is directly proportional to the utilization.

`JumpRateModelV2:` the Contract used to set up a complex interest rate model, which the interest rate jumps to a higher tier when the utilization rate exceeds u optimal.

### Price Oracle Contract
`Price Oracle:` the JustLend Protocol use Chainlink's price service to fetch the token price. The PriceOracle contract is responsible for setting and display token prices.

### Governance Contract
`GovernorBravo:` The main JustLend Governance Contract. Users interact with it to:
- Submit new proposal
- Vote on a proposal
- Cancel a proposal
- Queue a proposal for execution with a time lock executor contract

`Timelock:` the contract used to execute or cancel a queued transaction.

### Comptroller Contract
`Comptroller:` the Comptroller contract is the central contract for each lending pool. It contains functionality central to borrowing activity in the pool like supplying and borrowing assets and liquidations.


## **Staked TRX Contracts**
`Staked TRX(sTRX):` the contract utilized for staking TRX to earn high rewards.

## **Energy Rental**
`Energy Rental:` contracts enable users to rent energy anytime with a low price.

