# Price Oracle

Blockchain-powered smart contracts, by their inherent design, cannot directly access information from external systems. To bridge this critical gap and ensure the integrity of financial operations, the JustLend DAO protocol relies on robust and decentralized price feeds.
We secure various markets by leveraging a multi-source price aggregation strategy, utilizing [Chainlink](https://chain.link/) Data Feeds, [WinkLink](https://winklink.org/#/home)Data Feeds, and [SUN.io](https://sun.io/#/home) DEX as price sources. The prices from all three sources are aggregated offchain before feeding the accurate token valuation.

`SimplePriceOracle.sol:` allows users to:

* Price Poster
* Get Asset Price
* Set Price

The source code is available on [Github](https://github.com/justlend/justlend-protocol/blob/main/contracts/SimplePriceOracle.sol).


## **Contracts ABI**




