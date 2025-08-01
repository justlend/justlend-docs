# Price Oracle

Blockchain-powered smart contracts, by design, cannot access external market data directly. To ensure accurate and tamper-resistant pricing, the JustLend DAO protocol relies on a multi-source data aggregation system that draws from reputable and decentralized sources.

[Chainlink](https://chain.link/) Data Feeds are the key component of this process, helping to strengthen the security and reliability of pricing across markets.


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
