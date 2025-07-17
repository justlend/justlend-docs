# Comptroller

The Comptroller is the risk management module of the JustLend DAO protocol. It determines how much collateral should users keep to avoid liquidation.
The Comptroller is implemented as an upgradable contract. The entrance is [Unitroller](https://tronscan.org/#/contract/TGjYzgCyPobsNS9n6WcbdLVR9dH7mWqFx7/code); the implementation is [Comptroller](https://tronscan.org/#/contract/TJZi9eWzCLGBi9tuwvPxnaZTGa2iUpRc8v/code).

`Comptroller.sol:` allows users to:

* Markets
* Get Assets In
* Get Account Liquidation
* Liquidation Incentive

The source code is available on [Github](https://github.com/justlend/justlend-protocol/blob/main/contracts/Comptroller.sol).


## **Markets**

### **Enter Markets**
Calling this method enters a list of markets to supply or borrow.
``` solidity
function enterMarkets(address[] memory cTokens) public returns (uint[] memory)
```

* **Parameter description:**
    * `cTokens:` address list of the markets to enter.
* **Returns:** for each market, returns 0 for success, otherwise an error code.


### **Exit Market**
Calling this method exits a currently entered market.
``` solidity
function exitMarket(address cTokenAddress) external returns (uint)
```

* **Parameter description:**
    * `cTokenAddress:` market address to quit.
* **Returns:** 0 on success, otherwise an error code.


### **Get Assets In**
Calling this method returns a list of already entered markets.
``` solidity
function getAssetsIn(address account) external view returns (CToken[] memory)
```

* **Parameter description:**
    * `account:` the markets this account enters will be returned.
* **Returns:** markets have been entered by the specified address.


### **Markets**
Calling this method returns the status of a market(isListed, collateralFactorMantissa, comped)
``` solidity
function markets(address cTokenAddress) view returns (bool, uint, bool)
```

* **Parameter description:**
    * `cTokenAddress:` market address.
* **Returns:**
    * `isListed:` whether recognized by comptroller;
    * `collateralFactorMantissa:` the value can be borrowed(scaled by 1e18);
    * `comped:` whether suppliers & borrowers can get jst dividends.



## **Collateral & Liquidation**

### **Get Account Liquidity**
Calling this method returns the liquidity and shortfall of a user.
``` solidity
function getAccountLiquidity(address account) public view returns (uint, uint, uint)
```

* **Parameter description:**
  * `account:` address to be queried.
* **Returns:**
  * `error:` 0 for success, otherwise an error code;
  * `liquidity:` current liquidity;
  * `shortfall:` the shortfall value of the account's collateral requirement.


### **Close Factor Mantissa**
Calling this method gets the percentage of a liquidatable account should repay in a single liquidation. The range is 0%-100%. The calculation result of this method applies to a single asset.
``` solidity
function closeFactorMantissa() view returns (uint256)
```

* **Parameter description:** N/A.
* **Returns:** The close factor, scaled by 1e18.


### **Liquidation Incentive Mantissa**
Calling this method gets liquidators' incentives. The incentive is for underwater accounts. Part of this will be given to jToken reserves according to the seize share.
``` solidity
function liquidationIncentiveMantissa() view returns (uint256)
```

* **Parameter description:** N/A.
* **Returns:** The close factor, scaled by 1e18.

