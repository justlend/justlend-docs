---
title: SBM — Supply & Borrow Market contracts
description: JustLend DAO core lending contract reference — jToken (`CErc20Delegator`) function signatures for mint, borrow, repayBorrow, redeem, liquidateBorrow, with TronWeb examples and error codes.
---

# SBM

!!! info "Units & precision"
    * Amounts passed to `mint`/`borrow`/`repayBorrow`/`redeemUnderlying` are in the **underlying's smallest unit** — always read `decimals()` on the underlying TRC20 first. TRX = 6, USDT = 6, USDC = 6, USDD = 18, BTC/WBTC = 8, ETH = 18.
    * jToken amounts (`redeem`, `transfer`, `balanceOf`) are in **8 decimals** regardless of the underlying.
    * Rates (`borrowRatePerBlock`, `supplyRatePerBlock`) and the exchange rate are scaled by **`1e18`**, per-block.
    * Network in all examples below is **TRON Mainnet**. Test on Nile first.

!!! warning "TRC20 `approve()` race condition (USDT-style underlyings)"
    Several TRC20s used as JustLend underlyings — notably **TRON USDT** (`TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t`) — are non-standard implementations that **reject `approve(spender, newAmount)` if the current allowance is non-zero**. If a previous `approve()` left a residual allowance, the next call will revert with `SafeERC20: approve from non-zero to non-zero allowance` (or its TRC20 equivalent), and the subsequent `mint`/`repayBorrow` will fail to pull funds.

    **Safe pattern** before every `mint(uint)` / `repayBorrow(uint)` / `liquidateBorrow(...)` on jUSDT / jUSDCOLD / jTUSD / jUSDDOLD / jBUSDOLD-style markets:

    ```javascript
    // 1. Read the current allowance
    const current = await usdt.methods.allowance(user, jUSDT).call();
    // 2. If non-zero AND different from the target, zero it first
    if (current !== '0' && current !== targetAmount) {
        await usdt.methods.approve(jUSDT, 0).send({ from: user });
    }
    // 3. Set the actual allowance
    await usdt.methods.approve(jUSDT, targetAmount).send({ from: user });
    ```

    Standard-compliant TRC20s (e.g. USDD, BTC, WBTC, sTRX) do not have this constraint, but using the safe pattern unconditionally costs only one extra `approve(0)` when an actual change is needed — cheap insurance.

The JustLend DAO Supply and Borrow Market (SBM) is a decentralized  liquidity pool where users can participate as suppliers, borrowers or liquidators. Suppliers provide liquidity to a market and can earn interest on the assets provided, where borrowers are able to borrow in a collateralize assets way.

The SBM contract is the main user-facing contract. Most user interactions with the JustLend DAO Protocol occur via the Ctoken contract. It exposes the liquidity management methods that can be invoked using either Solidity or Web3 libraries.

`Ctoken.sol:` allows users to:

* Supply
* Borrow
* Withdraw
* Repay
* Liquidation

The source code is available on [Github](https://github.com/justlend/justlend-protocol/blob/main/contracts/CToken.sol).

&emsp;

<a id="query-interface"></a>

## **Query Interface**

<a id="exchange-rate"></a>

### **ExchangeRate**
Calling this method accrues interest and returns the up-to-date exchange rate.
``` solidity
function exchangeRateCurrent() public nonReentrant returns (uint)
```

* **Parameter description:** N/A
* **Returns:** calculated exchange rate scaled by 1e18.


### **Get Cash**
Calling this method gets the total amount of underlying balance currently available to this market.
``` solidity
function getCash() public view returns (uint)
```

* **Parameter description:** N/A
* **Returns:** The quantity of underlying assets owned by this contract.


### **Total Borrows**
Calling this method gets the sum of the currently loaned-outs and the accrued interests.
``` solidity
function totalBorrowsCurrent() external nonReentrant returns (uint)
```

* **Parameter description:** N/A
* **Returns:** The total borrows with interest.


### **Borrow Balance**
Calling this method accrues interest to the updated borrowIndex and then calculates the account's borrow balance using the updated borrowIndex.
``` solidity
function borrowBalanceCurrent(address account) external nonReentrant returns (uint)
```

* **Parameter description:**
    * `account:` the address whose balance should be calculated after updating borrowIndex.
* **Returns:** The total borrows with interest.


<a id="borrow-rate"></a>

### **Borrow Rate**
Calling this method gets the current per-block borrow interest rate for this jToken.
``` solidity
function borrowRatePerBlock() external view returns (uint)
```

* **Parameter description:** N/A
* **Returns:** The borrow interest rate per block, scaled by 1e18.


### **Total Supply**
Calling this method gets the total number of tokens in circulation.
``` solidity
function totalSupply() external view returns (uint256)
```

* **Parameter description:** N/A
* **Returns:** The supply of tokens.


<a id="underlying-balance"></a>

### **Underlying Balance**
Calling this method gets the underlying balance of the owner.
``` solidity
function balanceOfUnderlying(address owner) external returns (uint)
```

* **Parameter description:**
    * `owner:` the address of the account.
* **Returns:** The amount of underlying owned by owner.


<a id="supply-rate"></a>

### **Supply Rate**
Calling this method gets the current per-block supply interest rate for this jToken.
``` solidity
function supplyRatePerBlock() external view returns (uint)
```

* **Parameter description:** N/A
* **Returns:** The supply interest rate per block, scaled by 1e18.


### **Total Reserves**
Calling this method gets the reserves. Reserve represents a portion of historical interest set aside as cash which can be withdrawn or transferred through the protocol's governance.
``` solidity
function totalReserves() returns (uint)
```

* **Parameter description:** N/A
* **Returns:** The total amount of reserves.


### **Reserve Factor**
Calling this method gets the current reserve factor.
``` solidity
function reserveFactorMantissa() returns (uint)
```

* **Parameter description:** N/A
* **Returns:** The current reserve factor.

&emsp;

<a id="write-interface"></a>

## **Write Interface**

<a id="borrow"></a>

### **Borrow**
Calling this method borrows assets from JustLend DAO protocol to the sender's owner address.
``` solidity
function borrow(uint borrowAmount) external returns (uint)
```

* **Parameter description:**
    * `borrowAmount:` the amount of the underlying asset to borrow.
* **Returns:** None, reverts on error.

#### **Event**
``` solidity
Borrow(address borrower, uint borrowAmount, uint accountBorrows, uint totalBorrows, uint borrowIndex)
```

* Emits when user successfully borrow.
    * `borrower:` address of borrow assets account;
    * `borrowAmount:` the amount of borrowed assets;
    * `accountBorrows:` the account borrow the assets;
    * `totalBorrows:` total borrow assets form the account;
    * `borrowIndex:` the index of this borrow order.


<a id="repayborrow"></a>

### **repayBorrow**
Calling this method repays their own borrow.
``` solidity
function repayBorrow(uint amount) external payable
```

* **Parameter description:**
    * `amount:` the amount of the asset to repay.
* **Returns:** None, reverts on error.

#### **Event**
``` solidity
RepayBorrow(address payer, address borrower, uint repayAmount, uint accountBorrows, uint totalBorrows, uint borrowIndex)
```

* Emits when user successfully repay borrow.
    * `payer:` operate repay borrow;
    * `borrower:` address of borrow assets account;
    * `repayAmount:` the amount of repaid assets;
    * `accountBorrows:` the account borrow the assets;
    * `totalBorrows:` total borrow assets form the account;
    * `borrowIndex:` the index of this borrow order.


<a id="repayborrowbehalf"></a>

### **repayBorrowBehalf**
Calling this method repays their own borrow.
``` solidity
function repayBorrow(uint amount) external payable
```

* **Parameter description:**
    * `borrower:` the account with the debt being paid off.
    * `msg.value:` the amount to repay.
* **Returns:** None, reverts on error.


<a id="mint"></a>

### **Mint**
Calling this method supplies assets into the market and receives jTokens in exchange.
``` solidity
function mint() external payable
```

* **Parameter description:**
    * `msg.value:` the amount of TRX to supply.
* **Returns:** None, reverts on error.

#### **Event**
``` solidity
Mint(address minter, uint mintAmount, uint mintTokens)
```

* Emits when user successfully mint.
    * `minter:` operate supply assets into the market;
    * `mintAmount:` the amount of supplied assets;
    * `mintTokens:` the tokens need to mint.


<a id="redeem"></a>

### **Redeem**
Calling this method redeems jTokens in exchange for the underlying asset and accrues interest whether or not the operation succeeds.
``` solidity
function redeem(uint redeemTokens) external returns (uint)
```

* **Parameter description:**
    * `redeemTokens:`  the number of jTokens to redeem into underlying.
* **Returns:** 0 for success, reverts on error.

#### **Event**
``` solidity
Redeem(address redeemer, uint redeemAmount, uint redeemTokens)
```

* Emits when user successfully redeem.
    * `redeemer:` operate redeem jTokens;
    * `redeemAmount:` the amount of redeem assets;
    * `redeemTokens:` the tokens need to redeem.


<a id="redeemunderlying"></a>

### **RedeemUnderlying**
Calling this method redeems jTokens in exchange for a specified amount of underlying asset.
``` solidity
function redeemUnderlying(uint redeemAmount) external returns (uint)
```

* **Parameter description:**
    * `redeemAmount:` the amount of underlying to redeem.
* **Returns:** 0 for success, reverts on error.


### **Transfer**
Calling this method transfers a specified amount of jtokens to the destination. This action will fail if the account's liquidity become negative due to the transfer.
``` solidity
function transfer(address dst, uint256 amount) external nonReentrant returns (bool)
```

* **Parameter description:**
    * `dst:` the receiver's address.
    * `amount:` amount of token to be transferred.
* **Returns:** A boolean value indicating whether or not the transfer succeeded.

&emsp;

<a id="liquidation-process"></a>

## **Liquidation Process**

To enable developers to determine if a user is eligible for liquidation and to facilitate the liquidation process through contract calls, the following steps outline the specific operations to be executed:

1. **Query Liquidation Incentive:** Before proceeding, check the reward of the liquidation. This represents the "bonus" collateral a liquidator receives.
    * **Action:** Call `liquidationIncentiveMantissa()` on the **Unitroller** contract.
    * **Purpose:** To calculate the potential profit from the liquidation.

2. **Assess Account Liquidity:** Identify whether an account's collateral is insufficient to cover its debt.
    * **Action:** Call `getAccountLiquidity(address account)` on the **Unitroller** contract.
    * **Evaluation:** This function returns three values. You are looking for the shortfall.
        * If **shortfall > 0:** The account is underwater and eligible for liquidation.
        * If **liquidity > 0:** The account is healthy and cannot be liquidated.

3. **Execute Liquidation:** Once a target is confirmed, call the specific entry point based on the asset type being repaid.
    * **For jTRC20:** Call `liquidateBorrow(address borrower, uint repayAmount, address jTokenCollateral)` on the respective jTrc20 contract.
    * **For jTRX:** Call `liquidateBorrow(address borrower, address jTokenCollateral)` on the jTRX contract.

In addition, JustLend DAO will continuously monitor relevant data and provide an interface for querying high-risk liquidation users. You can **Identify High-Risk Users** by navigating to the [APIs](https://docs.justlend.org/developers/apis/) page and calling the **/justlend/liquidate/highRiskAccountList** endpoint.

**Please note** that there may be a certain delay in the availability of backend data and is for reference only.

&emsp;

<a id="liquidation-incentive"></a>

### **Liquidation Incentive**
By calling the liquidationIncentiveMantissa function of the Unitroller contract, liquidation incentives can be inquired. Liquidators will be given a proportion of the borrower's collateral as an incentive, which is defined as liquidation incentive. This is to encourage liquidators to perform liquidation of underwater accounts.
``` solidity
function liquidationIncentiveMantissa() view returns (uint)
```

* **Parameter description:** N/A
* **Returns:** The liquidationIncentive, scaled by 1e18, is multiplied by the closed borrow amount from the liquidator to determine how much collateral can be seized.


<a id="get-account-liquidity"></a>

### **Get Account Liquidity**
By calling the getAccountLiquidity function of the Unitroller contract, account information can be accessed through an account's address to determine whether the account should be liquidated or not.
``` solidity
getAccountLiquidity(address account) view returns (uint, uint, uint)
```

* **Parameter description:**
    * `account:` user address.
* **Returns:** The amount of underlying owned by owner.
    * `error:` error code, 0 means success.
    * `liquidity:` liquidity.
    * `shortfall:` When the value is bigger than 0, the current account does not meet the market requirement for collateralization and needs to be liquidated.

Note: There should be at most one non-zero value between liquidity and shortfall.


<a id="liquidate-borrowjtrc20"></a>

### **Liquidate Borrow（jTrc20）**
By calling liquidateBorrow function of the corresponding jTrc20 contract (e.g. jUSDT), accounts whose liquidity does not meet the market requirement for collateralization will be liquidated by other users to restore the account liquidity to a normal level (i.e. higher than the market requirement for collateralization). In the event of liquidation, liquidators may repay part or 50% of the loan for the borrower. Liquidators will be given a proportion of the borrower's collateral as an incentive.
``` solidity
function liquidateBorrow(address borrower, uint repayAmount, address jTokenCollateral) returns (uint)
```

* **Parameter description:**
    * `borrower:` address of a liquidated account.
    * `repayAmount:` amount of token to be repaid in the event of liquidation (measured in the borrowed asset).
    * `jTokenCollateral:` address of the jTOKEN contract to set aside the collateralized asset of a borrower.
* **Returns:** 0 on success, otherwise an Error code.


<a id="liquidate-borrowjtrx"></a>

### **Liquidate Borrow（jTRX）**
By calling the liquidateBorrow function of the jTRX contract, accounts whose liquidity does not meet the market requirement for collateralization will be liquidated by other users to restore the account liquidity to a normal level (i.e., higher than the market requirement for collateralization). In the event of liquidation, liquidators may repay part or 50% of the loan for the borrower. Liquidators will be given a proportion of the borrower's collateral as an incentive.
``` solidity
function liquidateBorrow(address borrower, address jTokenCollateral) payable
```

* **Parameter description:**
    * `borrower:` address of a liquidated account.
    * `jTokenCollateral:` address of the jTRX contract to set aside the collateralized asset of a borrower.
    * `msg.value:` amount of TRX to be repaid in the event of liquidation.
* **Returns:** No return. If any error occurs, the transaction will be reverted.

#### **Event**
``` solidity
LiquidateBorrow(address liquidator, address borrower, uint repayAmount, address cTokenCollateral, uint seizeTokens)
```

* Emits when user successfully liquidate borrow order.
    * `liquidator:` operate liquidation;
    * `borrower:` address of a liquidated account;
    * `repayAmount:` the amount of repaid assets;
    * `cTokenCollateral:` address of the jTRX contract to set aside the collateralized asset of a borrower；
    * `seizeTokens:` the tokens need to be liquidated.

&emsp;

<a id="examples-tronweb"></a>

## **Examples (TronWeb)**

The snippets below use [TronWeb](https://developers.tron.network/reference/tronweb-object). Replace the `// PRIVATE_KEY=…` literal with your own loading mechanism — **never commit a key**. All addresses below are TRON Mainnet.

### Setup

```javascript
const TronWeb = require('tronweb');

const tronWeb = new TronWeb({
  fullHost: 'https://api.trongrid.io',
  headers: { 'TRON-PRO-API-KEY': process.env.TRONGRID_API_KEY }, // strongly recommended
  privateKey: process.env.PRIVATE_KEY,
});

const UNITROLLER = 'TGjYzgCyPobsNS9n6WcbdLVR9dH7mWqFx7'; // Comptroller proxy
const JUSDT      = 'TXJgMdjVX5dKiQaUi9QobwNxtSQaFqccvd'; // jUSDT CErc20Delegator
const JTRX       = 'TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP'; // jTRX
const USDT       = 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'; // USDT underlying
```

### 1. Supply USDT — `approve` → `mint`

```javascript
async function supplyUSDT(amountWithDecimals /* e.g. "1000000000" for 1,000 USDT */) {
  const usdt  = await tronWeb.contract().at(USDT);
  const jusdt = await tronWeb.contract().at(JUSDT);

  // 1. Approve the jUSDT contract to pull USDT from this wallet.
  //    Skip if you've already approved a sufficient amount.
  await usdt.approve(JUSDT, amountWithDecimals).send();

  // 2. Mint jUSDT (supply USDT). Returns 0 on success.
  const txId = await jusdt.mint(amountWithDecimals).send({
    feeLimit: 200_000_000, // 200 TRX feeLimit
  });
  console.log('mint tx:', txId);
}
```

### 2. Supply TRX — `mint()` (payable, no approval needed)

```javascript
async function supplyTRX(amountInSun /* 1 TRX = 1_000_000 sun */) {
  const jtrx = await tronWeb.contract().at(JTRX);

  const txId = await jtrx.mint().send({
    callValue: amountInSun,
    feeLimit: 200_000_000,
  });
  console.log('mint tx:', txId);
}
```

### 3. Enable supplied asset as collateral — `enterMarkets`

!!! warning "Required before borrowing"
    Supplying alone does **not** make the asset count as collateral. You must call `enterMarkets` on the Unitroller with the **jToken** addresses you want enabled.

```javascript
async function enableCollateral(jTokens /* e.g. [JUSDT, JTRX] */) {
  const comptroller = await tronWeb.contract().at(UNITROLLER);
  const txId = await comptroller.enterMarkets(jTokens).send({ feeLimit: 200_000_000 });
  console.log('enterMarkets tx:', txId);
}
```

### 4. Borrow TRX against existing collateral

```javascript
async function borrowTRX(amountInSun) {
  const jtrx = await tronWeb.contract().at(JTRX);

  // Pre-flight: confirm the account has positive liquidity (no shortfall)
  const comptroller = await tronWeb.contract().at(UNITROLLER);
  const [error, liquidity, shortfall] = await comptroller
    .getAccountLiquidity(tronWeb.defaultAddress.base58)
    .call();
  if (error.toString() !== '0' || shortfall.toString() !== '0') {
    throw new Error('account is not healthy enough to borrow');
  }

  const txId = await jtrx.borrow(amountInSun).send({ feeLimit: 200_000_000 });
  console.log('borrow tx:', txId);
}
```

### 5. Repay USDT — `approve` → `repayBorrow`

```javascript
async function repayUSDT(amountWithDecimals /* underlying smallest unit */) {
  const usdt  = await tronWeb.contract().at(USDT);
  const jusdt = await tronWeb.contract().at(JUSDT);

  await usdt.approve(JUSDT, amountWithDecimals).send();

  // Pass uint256(-1) for a full repayment
  const txId = await jusdt.repayBorrow(amountWithDecimals).send({ feeLimit: 200_000_000 });
  console.log('repay tx:', txId);
}
```

### 6. Redeem (withdraw) — by jToken units or by underlying

```javascript
// Redeem by jToken units (8 decimals)
async function redeemJUSDT(jTokens /* in 8 decimals */) {
  const jusdt = await tronWeb.contract().at(JUSDT);
  return jusdt.redeem(jTokens).send({ feeLimit: 200_000_000 });
}

// Redeem an exact underlying amount (in underlying's decimals)
async function redeemUSDTExact(amountWithDecimals) {
  const jusdt = await tronWeb.contract().at(JUSDT);
  return jusdt.redeemUnderlying(amountWithDecimals).send({ feeLimit: 200_000_000 });
}
```

### 7. APY conversion from per-block rates

```javascript
const BLOCKS_PER_YEAR = 10_512_000n; // ~3s blocks
const SCALE = 10n ** 18n;

async function apys(jTokenAddr) {
  const jt = await tronWeb.contract().at(jTokenAddr);
  const [supplyRate, borrowRate] = await Promise.all([
    jt.supplyRatePerBlock().call(),
    jt.borrowRatePerBlock().call(),
  ]);
  // Simple (non-compounded) annualized rate as a decimal
  const supplyAPR = Number(BigInt(supplyRate) * BLOCKS_PER_YEAR) / Number(SCALE);
  const borrowAPR = Number(BigInt(borrowRate) * BLOCKS_PER_YEAR) / Number(SCALE);
  return { supplyAPR, borrowAPR };
}
```

For mining-reward-inclusive APY, prefer the API field `supplyApy` on `GET /lend/jtoken`.

&emsp;



## **Error Code And Failure info**

### **Error code**
| Code | Name                           | Description                                                                                                                                                                  |
|------|--------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0    | NO_ERROR                       | Not a failure.                                                                                                                                                               |
| 1    | UNAUTHORIZED                   | The sender is not authorized to perform this action.                                                                                                                         |
| 2    | BAD_INPUT                      | An invalid argument was supplied by the caller.                                                                                                                              |
| 3    | COMPTROLLER_REJECTION          | The action would violate the comptroller policy.                                                                                                                             |
| 4    | COMPTROLLER_CALCULATION_ERROR  | An internal calculation has failed in the comptroller.                                                                                                                       |
| 5    | INTEREST_RATE_MODEL_ERROR      | The interest rate model returned an invalid value.                                                                                                                           |
| 6    | INVALID_ACCOUNT_PAIR           | The specified combination of accounts is invalid.                                                                                                                            |
| 7    | INVALID_CLOSE_AMOUNT_REQUESTED | The amount to liquidate is invalid.                                                                                                                                          |
| 8    | INVALID_COLLATERAL_FACTOR      | The collateral factor is invalid.                                                                                                                                            |
| 9    | MATH_ERROR                     | A math calculation error occurred.                                                                                                                                           |
| 10   | MARKET_NOT_FRESH               | Interest has not been properly accrued.                                                                                                                                      |
| 11   | MARKET_NOT_LISTED              | The market is not currently listed by its comptroller.                                                                                                                       |
| 12   | TOKEN_INSUFFICIENT_ALLOWANCE   | ERC-20 contract must allow Money Market contract to call transferFrom. The current allowance is either 0 or less than the requested supply, repayBorrow or liquidate amount. |
| 13   | TOKEN_INSUFFICIENT_BALANCE     | Caller does not have sufficient balance in the ERC-20 contract to complete the desired action.                                                                               |
| 14   | TOKEN_INSUFFICIENT_CASH        | The market does not have a sufficient cash balance to complete the transaction. You may attempt this transaction again later.                                                |
| 15   | TOKEN_TRANSFER_IN_FAILED       | Failure in ERC-20 when transfering token into the market.                                                                                                                    |
| 16   | TOKEN_TRANSFER_OUT_FAILED      | Failure in ERC-20 when transfering token out of the market.                                                                                                                  |


### **Failure info**
| Code | Name                                                       |
|------|------------------------------------------------------------|
| 0    | ACCEPT_ADMIN_PENDING_ADMIN_CHECK                           |
| 1    | ACCRUE_INTEREST_ACCUMULATED_INTEREST_CALCULATION_FAILED    |
| 2    | ACCRUE_INTEREST_BORROW_RATE_CALCULATION_FAILED             |
| 3    | ACCRUE_INTEREST_NEW_BORROW_INDEX_CALCULATION_FAILED        |
| 4    | ACCRUE_INTEREST_NEW_TOTAL_BORROWS_CALCULATION_FAILED       |
| 5    | ACCRUE_INTEREST_NEW_TOTAL_RESERVES_CALCULATION_FAILED      |
| 6    | ACCRUE_INTEREST_SIMPLE_INTEREST_FACTOR_CALCULATION_FAILED  |
| 7    | BORROW_ACCUMULATED_BALANCE_CALCULATION_FAILED              |
| 8    | BORROW_ACCRUE_INTEREST_FAILED                              |
| 9    | BORROW_CASH_NOT_AVAILABLE                                  |
| 10   | BORROW_FRESHNESS_CHECK                                     |
| 11   | BORROW_NEW_TOTAL_BALANCE_CALCULATION_FAILED                |
| 12   | BORROW_NEW_ACCOUNT_BORROW_BALANCE_CALCULATION_FAILED       |
| 13   | BORROW_MARKET_NOT_LISTED                                   |
| 14   | BORROW_COMPTROLLER_REJECTION                               |
| 15   | LIQUIDATE_ACCRUE_BORROW_INTEREST_FAILED                    |
| 16   | LIQUIDATE_ACCRUE_COLLATERAL_INTEREST_FAILED                |
| 17   | LIQUIDATE_COLLATERAL_FRESHNESS_CHECK                       |
| 18   | LIQUIDATE_COMPTROLLER_REJECTION                            |
| 19   | LIQUIDATE_COMPTROLLER_CALCULATE_AMOUNT_SEIZE_FAILED        |
| 20   | LIQUIDATE_CLOSE_AMOUNT_IS_UINT_MAX                         |
| 21   | LIQUIDATE_CLOSE_AMOUNT_IS_ZERO                             |
| 22   | LIQUIDATE_FRESHNESS_CHECK                                  |
| 23   | LIQUIDATE_LIQUIDATOR_IS_BORROWER                           |
| 24   | LIQUIDATE_REPAY_BORROW_FRESH_FAILED                        |
| 25   | LIQUIDATE_SEIZE_BALANCE_INCREMENT_FAILED                   |
| 26   | LIQUIDATE_SEIZE_BALANCE_DECREMENT_FAILED                   |
| 27   | LIQUIDATE_SEIZE_COMPTROLLER_REJECTION                      |
| 28   | LIQUIDATE_SEIZE_LIQUIDATOR_IS_BORROWER                     |
| 29   | LIQUIDATE_SEIZE_TOO_MUCH                                   |
| 30   | MINT_ACCRUE_INTEREST_FAILED                                |
| 31   | MINT_COMPTROLLER_REJECTION                                 |
| 32   | MINT_EXCHANGE_CALCULATION_FAILED                           |
| 33   | MINT_EXCHANGE_RATE_READ_FAILED                             |
| 34   | MINT_FRESHNESS_CHECK                                       |
| 35   | MINT_NEW_ACCOUNT_BALANCE_CALCULATION_FAILED                |
| 36   | AMINT_NEW_TOTAL_SUPPLY_CALCULATION_FAILED                  |
| 37   | MINT_TRANSFER_IN_FAILED                                    |
| 38   | MINT_TRANSFER_IN_NOT_POSSIBLE                              |
| 39   | REDEEM_ACCRUE_INTEREST_FAILED                              |
| 40   | REDEEM_COMPTROLLER_REJECTION                               |
| 41   | REDEEM_EXCHANGE_TOKENS_CALCULATION_FAILED                  |
| 42   | REDEEM_EXCHANGE_AMOUNT_CALCULATION_FAILED                  |
| 43   | REDEEM_EXCHANGE_RATE_READ_FAILED                           |
| 44   | REDEEM_FRESHNESS_CHECK                                     |
| 45   | REDEEM_NEW_ACCOUNT_BALANCE_CALCULATION_FAILED              |
| 46   | REDEEM_NEW_TOTAL_SUPPLY_CALCULATION_FAILED                 |
| 47   | REDEEM_TRANSFER_OUT_NOT_POSSIBLE                           |
| 48   | REDUCE_RESERVES_ACCRUE_INTEREST_FAILED                     |
| 49   | REDUCE_RESERVES_ADMIN_CHECK                                |
| 50   | REDUCE_RESERVES_CASH_NOT_AVAILABLE                         |
| 51   | REDUCE_RESERVES_FRESH_CHECK                                |
| 52   | REDUCE_RESERVES_VALIDATION                                 |
| 53   | REPAY_BEHALF_ACCRUE_INTEREST_FAILED                        |
| 54   | REPAY_BORROW_ACCRUE_INTEREST_FAILED                        |
| 55   | REPAY_BORROW_ACCUMULATED_BALANCE_CALCULATION_FAILED        |
| 56   | REPAY_BORROW_COMPTROLLER_REJECTION                         |
| 57   | REPAY_BORROW_FRESHNESS_CHECK                               |
| 58   | REPAY_BORROW_NEW_ACCOUNT_BORROW_BALANCE_CALCULATION_FAILED |
| 59   | REPAY_BORROW_NEW_TOTAL_BALANCE_CALCULATION_FAILED          |
| 60   | REPAY_BORROW_TRANSFER_IN_NOT_POSSIBLE                      |
| 61   | SET_COLLATERAL_FACTOR_OWNER_CHECK                          |
| 62   | SET_COLLATERAL_FACTOR_VALIDATION                           |
| 63   | SET_COMPTROLLER_OWNER_CHECK                                |
| 64   | SET_INTEREST_RATE_MODEL_ACCRUE_INTEREST_FAILED             |
| 65   | SET_INTEREST_RATE_MODEL_FRESH_CHECK                        |
| 66   | SET_INTEREST_RATE_MODEL_OWNER_CHECK                        |
| 67   | SET_MAX_ASSETS_OWNER_CHECK                                 |
| 68   | SET_ORACLE_MARKET_NOT_LISTED                               |
| 69   | SET_PENDING_ADMIN_OWNER_CHECK                              |
| 70   | SET_RESERVE_FACTOR_ACCRUE_INTEREST_FAILED                  |
| 71   | SET_RESERVE_FACTOR_ADMIN_CHECK                             |
| 72   | SET_RESERVE_FACTOR_FRESH_CHECK                             |
| 73   | SET_RESERVE_FACTOR_BOUNDS_CHECK                            |
| 74   | TRANSFER_COMPTROLLER_REJECTION                             |
| 75   | TRANSFER_NOT_ALLOWED                                       |
| 76   | TRANSFER_NOT_ENOUGH                                        |
| 77   | TRANSFER_TOO_MUCH                                          |
