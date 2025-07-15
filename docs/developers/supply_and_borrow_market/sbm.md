# SBM

The JustLend DAO Supply and Borrow Market (SBM) is a decentralized  liquidity pool where users can participate as suppliers, borrowers or liquidators. Suppliers provide liquidity to a market and can earn interest on the assets provided, where borrowers are able to borrow in a collateralize assets way.

The SBM contract is the main user-facing contract. Most user interactions with the JustLend DAO Protocol occur via the Ctoken contract. It exposes the liquidity management methods that can be invoked using either Solidity or Web3 libraries.

`Ctoken.sol:` allows users to:

* Supply
* Borrow
* Withdraw
* Reapy
* Liquidation

The source code is available on [Github](https://github.com/justlend/justlend-protocol/blob/main/contracts/CToken.sol).


## **Query Interface**

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

### **Underlying Balance**
Calling this method gets the underlying balance of the owner.
``` solidity
function balanceOfUnderlying(address owner) external returns (uint)
```
* **Parameter description:**
    * `owner:` the address of the account.
* **Returns:** The amount of underlying owned by owner.

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

### **Liquidation Incentive**
By calling the liquidationIncentiveMantissa function of the Unitroller contract, liquidation incentives can be inquired. Liquidators will be given a proportion of the borrower's collateral as an incentive, which is defined as liquidation incentive. This is to encourage liquidators to perform liquidation of underwater accounts.
``` solidity
function liquidationIncentiveMantissa() view returns (uint)
```
* **Parameter description:** N/A
* **Returns:** The liquidationIncentive, scaled by 1e18, is multiplied by the closed borrow amount from the liquidator to determine how much collateral can be seized.

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



## **Write Interface**


## **Error Code And Failure info**
