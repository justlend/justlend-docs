---
title: Contracts Overview
description: Architecture summary of every JustLend DAO contract on TRON — SBM jTokens, Comptroller, interest rate models, price oracle, governance, sTRX, Energy Rental — with proxy mode, ABI links, and key functions in one table.
---

# Contracts Overview

!!! info "About this page"
    * **Protocol:** JustLend DAO
    * **Network:** TRON Mainnet (Base58 addresses; see [`/developers/contracts.json`](contracts.json) for Mainnet + Nile addresses in Base58, EVM `0x` hex, and TRON-internal `41` hex) 
    * **Architecture:** Compound V2 fork
    * **Markets:** 17 active + 6 legacy = 23 jToken markets (authoritative list: [APIs §2](apis.md#2-jtoken-address-reference)) 
    * **Upgrade pattern:** every contract listed below is either `Delegator → Delegate` (proxy + implementation, **upgradeable** by Governance) or **immutable**, explicitly tagged in the table. The page first gives a one-screen machine-readable summary table; deeper per-component prose follows.
    

## Architecture summary

JustLend DAO Protocol contracts are divided in these repositories:

* **Supply and Borrow Market:** contains core contracts for JustLend DAO, including logic for supply and borrow market (SBM), supply and borrow market V2 (SBM V2), interest rate model, governance, price oracle and comptroller.
  * **SBM:** enables supplying of crypto assets as collateral in order to borrow the base asset. Accounts can also earn interest by supplying the base asset to the protocol.
  * **SBM V2:** an isolated-collateral lending protocol with a dual-layer structure of Vaults and Markets, along with an Adaptive Curve Interest Rate Model (IRM) for dynamic rate adjustment.
  * **Interest Rate Model:** users with a positive balance of the base asset earn interest, denominated in the base asset, based on a supply rate model.
  * **Price-Oracle:** contains the price oracle contracts we support, along with the logic validation for prices returned by these oracles.
  * **Governance:** contracts used for proposing, voting and executing proposals.
  * **Comptroller:** the risk management layer of the protocol. It determines how much collateral a user is required to maintain, and whether user can be liquidated.
* **Staked TRX:** the contracts utilized for staking TRX to earn high rewards.
* **Energy Rental:** contracts enable users to rent energy anytime with a low price.


## **Core Contracts**

### There are 5 categories of core repository contracts in SBM:

* JTokens Contract
* Interest Rate Model Contract
* Price Oracle Contract
* Governance Contract
* Comptroller Contract

#### JTokens Contract
`JToken:` the contract used to support all assets by JustLend DAO, such as the jTRX, jUSDT, jSUN and jBTC you receive after supplying the corresponding assets.

#### Interest Rate Model Contract
`WhitePaperInterestRateModel:` the contract used to set up a straightforward interest rate model, which the borrowing rate is directly proportional to the utilization.

`JumpRateModelV2:` the Contract used to set up a complex interest rate model, which the interest rate jumps to a higher tier when the utilization rate exceeds u optimal.

#### Price Oracle Contract
`Price Oracle:` the JustLend Protocol use Chainlink's price service to fetch the token price. The PriceOracle contract is responsible for setting and display token prices.

#### Governance Contract
`GovernorBravo:` The main JustLend Governance Contract. Users interact with it to:
- Submit new proposal
- Vote on a proposal
- Cancel a proposal
- Queue a proposal for execution with a time lock executor contract

`Timelock:` the contract used to execute or cancel a queued transaction.

#### Comptroller Contract
`Comptroller:` the Comptroller contract is the central contract for each lending pool. It contains functionality central to borrowing activity in the pool like supplying and borrowing assets and liquidations.


### There are 5 categories of core repository contracts in SBM V2:

* Moolah Market
* Moolah Vault
* TRX Provider
* Resilient Oracle
* Interest Rate Model

#### Moolah Market
`Moolah Market:` the Moolah Lending Market adopts an isolated-collateral lending protocol, where each market supports a single collateral asset paired with a single borrowable asset.

#### Moolah Vault
`Moolah Vault:` each Vault serves as a single-asset management contract that provides liquidity to various lending markets.

#### TRX Provider
`TRX Provider:` users can directly interact with the system using TRX through the TRXProvider module. The TRXProvider internally handles the conversion between TRX and WTRX, allowing seamless user operations such as deposits and withdrawals.

#### Resilient Oracle
`Resilient Oracle:` an aggregated price feed contract that supports up to three price sources for each token. It provides reliable on-chain price data with 18-decimal precision and allows users or protocols to query the latest price of any supported token. 

#### Interest Rate Model
`IRM:` the Adaptive Curve Interest Rate Model. It builds upon the Jump Curve model used in JustLend DAO V1, but adds dynamic adaptability, allowing real-time rate adjustments to keep market utilization near an optimal level.


## **Staked TRX Contracts**
`Staked TRX(sTRX):` the contract utilized for staking TRX to earn high rewards.

## **Energy Rental**
`Energy Rental:` contracts enable users to rent energy anytime with a low price.


## Contract summary table (machine-readable)

Single row per contract. Use this when integrating; treat the prose sections below as commentary.

| Component | Contract | Mainnet address (Base58) | Upgradeable? | Proxy mode | Key functions | ABI | Doc |
|-----------|----------|--------------------------|--------------|------------|---------------|-----|-----|
| Comptroller | `Unitroller` (entrypoint) | [`TGjYzgCyPobsNS9n6WcbdLVR9dH7mWqFx7`](https://tronscan.org/#/contract/TGjYzgCyPobsNS9n6WcbdLVR9dH7mWqFx7) | **Yes** (impl behind proxy) | Compound `Unitroller` (`_setPendingImplementation` + `_acceptImplementation`) | `enterMarkets`, `exitMarket`, `getAccountLiquidity`, `markets`, `closeFactorMantissa`, `liquidationIncentiveMantissa` | [`comptroller.json`](abis/comptroller.json) | [Comptroller](supply_and_borrow_market/comptroller.md) |
| Comptroller | `Comptroller` (implementation) | [`TB23wYojvAsSx6gR8ebHiBqwSeABiBMPAr`](https://tronscan.org/#/contract/TB23wYojvAsSx6gR8ebHiBqwSeABiBMPAr) | Replaced via `Unitroller` | Implementation only | — (delegated through `Unitroller`) | [`comptroller.json`](abis/comptroller.json) | [Comptroller](supply_and_borrow_market/comptroller.md) |
| SBM (TRX market) | `CErc20Delegator` (jTRX) | [`TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP`](https://tronscan.org/#/contract/TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP) | **Yes** (impl behind delegator) | Compound `CErc20Delegator` (`_setImplementation`) | `mint()` (payable, TRX), `borrow`, `repayBorrow` (payable), `redeem`, `redeemUnderlying`, `liquidateBorrow` (payable) | [`jtoken.json`](abis/jtoken.json) (plus [`jtrx-mint.json`](abis/jtrx-mint.json), [`jtrx-repay.json`](abis/jtrx-repay.json) for TRX-specific payable variants) | [SBM](supply_and_borrow_market/sbm.md) |
| SBM (TRC20 markets) | `CErc20Delegator` (per market, 22 instances) | See [`apis.md §2`](apis.md#2-jtoken-address-reference) | **Yes** per market | Compound `CErc20Delegator` (`_setImplementation`) | `mint(uint)`, `borrow`, `repayBorrow(uint)`, `redeem`, `redeemUnderlying`, `liquidateBorrow(address, uint, address)` | [`jtoken.json`](abis/jtoken.json) | [SBM](supply_and_borrow_market/sbm.md), [Deployed Contracts](deployed_contracts.md) |
| Interest Rate Model | `WhitePaperInterestRateModel` (linear) | Per market — see [Deployed Contracts](deployed_contracts.md) | **No** (immutable per deployment; new model contract per parameter change) | None | `getBorrowRate(cash, borrows, reserves)`, `getSupplyRate(cash, borrows, reserves, reserveFactorMantissa)` | [`interest-rate-model.json`](abis/interest-rate-model.json) | [Interest Rate Model](supply_and_borrow_market/interest_rate_model.md) |
| Interest Rate Model | `JumpRateModelV2` (kinked) | Per market — see [Deployed Contracts](deployed_contracts.md) | **No** (immutable per deployment; new model contract per parameter change) | None | `getBorrowRate`, `getSupplyRate`, `multiplierPerBlock`, `jumpMultiplierPerBlock`, `kink`, `baseRatePerBlock` | [`interest-rate-model.json`](abis/interest-rate-model.json) | [Interest Rate Model](supply_and_borrow_market/interest_rate_model.md) |
| Price Oracle | `PriceOracleProxy` (entrypoint) | [`TCKp2AzuhzV4B4Ahx1ej4mvQgHZ1kH7F7k`](https://tronscan.org/#/contract/TCKp2AzuhzV4B4Ahx1ej4mvQgHZ1kH7F7k) | **Yes** (impl behind proxy) | Address-only proxy (governance updates implementation pointer) | `getUnderlyingPrice(cToken)` | [`price-oracle.json`](abis/price-oracle.json) | [Price Oracle](supply_and_borrow_market/price_oracle.md) |
| Price Oracle | `SimplePriceOracle` (implementation) | [`TMiNCmvD3zdsv6mk7niBU6NPBzVNjYMQTV`](https://tronscan.org/#/contract/TMiNCmvD3zdsv6mk7niBU6NPBzVNjYMQTV) | Replaced via proxy | Implementation only | `getPrice`, `assetPrices`, `setPrice` (poster-only) | [`price-oracle.json`](abis/price-oracle.json) | [Price Oracle](supply_and_borrow_market/price_oracle.md) |
| Governance | `GovernorBravoDelegator` (entrypoint) | [`TEqiF5JbhDPD77yjEfnEMncGRZNDt2uogD`](https://tronscan.org/#/contract/TEqiF5JbhDPD77yjEfnEMncGRZNDt2uogD) | **Yes** (impl behind delegator) | Compound `GovernorBravoDelegator` (`_setImplementation`) | `propose`, `queue`, `execute`, `cancel`, `castVote`, `castVoteWithReason`, `state`, `deposit` | [`governor-alpha.json`](abis/governor-alpha.json) (Governor ABI; the WJST escrow is `wjst.json`) | [Governance](supply_and_borrow_market/governance.md) |
| Governance | `GovernorBravoDelegate` (implementation) | [`TCiQTkxhzwSeXhRsNdHCvrxHRAvpjQn5Dt`](https://tronscan.org/#/contract/TCiQTkxhzwSeXhRsNdHCvrxHRAvpjQn5Dt) | Replaced via delegator | Implementation only | — (delegated) | [`governor-alpha.json`](abis/governor-alpha.json) | [Governance](supply_and_borrow_market/governance.md) |
| Governance | `Timelock` (executor) | [`TRWNvb15NmfNKNLhQpxefFz7cNjrYjEw7x`](https://tronscan.org/#/contract/TRWNvb15NmfNKNLhQpxefFz7cNjrYjEw7x) | **No** (constructor-fixed admin and delay) | None | `queueTransaction`, `executeTransaction`, `cancelTransaction` | — | [Governance](supply_and_borrow_market/governance.md) |
| Governance | `JST` (TRC20 governance token) | [`TCFLL5dx5ZJdKnWuesXxi1VPwjLVmWZZy9`](https://tronscan.org/#/contract/TCFLL5dx5ZJdKnWuesXxi1VPwjLVmWZZy9) | **No** (standard TRC20) | None | `transfer`, `approve`, `balanceOf` | [`trc20.json`](abis/trc20.json) | [Tokenomics](../governance/tokenomics.md) |
| Governance | `WJST` (voting-power escrow) | See [Deployed Contracts](deployed_contracts.md) | **No** | None | `deposit`, `withdraw`, vote-power tracking | [`wjst.json`](abis/wjst.json) | [Governance](supply_and_borrow_market/governance.md) |
| Staked TRX | `sTRX` (liquid-staking contract) | [`TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5`](https://tronscan.org/#/contract/TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5) | **No** (constructor-fixed; new contract on protocol upgrade) | None | `deposit()` (payable), `withdraw`, `withdrawExact`, `claim`, `claimAll`, `exchangeRate`, `balanceInTrx` | [`strx.json`](abis/strx.json) | [Staked TRX](staked_trx.md) |
| Energy Rental | `EnergyRental` market contract | [`TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd`](https://tronscan.org/#/contract/TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd) | **No** | None | `rentResource` (payable), `returnResource`, `returnResourceByReceiver`, `liquidate`, `getRentInfo`, `_rentalRate` | [`energy-market.json`](abis/energy-market.json), rate model in [`energy-rate-model.json`](abis/energy-rate-model.json) | [Energy Rental](energy_rental.md) |

**Inter-contract call flow (most common write path — supply + borrow):**

```
User EOA
  └─► CErc20Delegator (jToken)
        ├─ delegatecall ► CErc20Delegate (mint/borrow logic)
        ├─ staticcall   ► PriceOracleProxy.getUnderlyingPrice()
        ├─ call         ► InterestRateModel.getBorrowRate() / getSupplyRate()
        └─ call         ► Unitroller (Comptroller proxy)
                            └─ delegatecall ► Comptroller.mintAllowed / borrowAllowed
```

`enterMarkets` is a precondition for any supplied asset to count as collateral — it is called directly on the `Unitroller` entrypoint, not on the jToken.

**Version evolution (`JumpRateModelV2`):** each market's rate model is its own deployed contract instance (immutable). Updating parameters (kink, multipliers, baseRate) means deploying a fresh `JumpRateModelV2` contract and calling `_setInterestRateModel` on the jToken via Governance. Past instances remain on chain but unused.
