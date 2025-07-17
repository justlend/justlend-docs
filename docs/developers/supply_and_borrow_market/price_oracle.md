# Price Oracle

Blockchain-powered smart contracts, by their inherent design, cannot directly access information from external systems. To bridge this critical gap and ensure the integrity of financial operations, the JustLend DAO protocol relies on robust and decentralized price feeds.
We use [Chainlink](https://chain.link/) Data Feeds as our primary Oracles to secure various markets. JustLend DAO protocol uses a [PriceOracle](https://tronscan.org/#/contract/TD8bq1aFY8yc9nsD2rfqqJGDtkh7aPpEpr/code) contract to set and display token prices in sun(10^-6 TRX), scaled by 10^(tokenDecimal - 6).
Prices of the underlying tokens are posted every 30 minutes via `setPrice()` by a specified poster.

`SimplePriceOracle.sol:` allows users to:

* Price Poster
* Get Asset Price
* Set Price

The source code is available on [Github](https://github.com/justlend/justlend-protocol/blob/main/contracts/SimplePriceOracle.sol).


## **Contracts ABI**

### **Anchor Token Price**
Calling this methods returns the current price anchor of a specified token.
``` solidity
function anchors(address) view returns(uint256, uint256)
```

* **Parameter description:**
    * `token:` the address of the underlying token(e.g. TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t for USDT).
* **Returns:**
    * `period:` the current time period. Calculated as: current block height/ 600 (the TRON network produces approx. 600 blocks per 30 mins);
    * `priceMantissa:` token prices in sun(10^-6 TRX), scaled by 10^(tokenDecimal - 6).


### **Price Poster**
Calling this methods returns the current price poster.
``` solidity
function poster() view returns(address)
```

* **Parameter description:** N/A.
* **Returns:** Address of the current poster.


### **Asset Prices**
Calling this method returns the current price of the specified asset.
``` solidity
function assetPrices(address asset) public view returns (uint)
```

* **Parameter description:**
    * `asset:` the address of the token to query.
* **Returns:** the current price of the token in sun(10^-6 TRX), scaled by 10^(tokenDecimal - 6).


### **Get Price**
Calling this method returns the current price of the specified asset.
``` solidity
function getPrice(address asset) public view returns (uint)
```

* **Parameter description:**
    * `asset:` the address of the token to query.
* **Returns:** the current price of the token in sun(10^-6 TRX), scaled by 10^(tokenDecimal - 6).


### **Set Price (poster-only)**
Calling this methods set a token price for the current time period.
``` solidity
function setPrice(address asset, uint requestedPriceMantissa) public returns (uint)
```

* **Parameter description:**
  * `asset:` the address of the underlying token (e.g. TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t for USDT);
  * `requestedPriceMantissa:` new price, scaled by 10^27.
* **Returns:** 0 for success, otherwise an error code.
