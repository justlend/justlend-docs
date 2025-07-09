JustLend DAO is a cutting-edge money market protocol powered by TRON, designed to create fund pools with interest rates determined by an algorithm based on the supply and demand of TRON assets. The protocol involves two main roles: suppliers and borrowers, who engage directly with the platform to earn or pay floating interest rates.

Each money market on JustLend DAO represents a specific TRON asset, including TRX, TRC20 stablecoins like USDT, and other TRC20-based tokens. The platform features an open and transparent ledger that records all transactions and historical interest rates, ensuring transparency and trust among users.
<br>

## **Core Architecture of JustLend DAO**

![architecture](https://raw.githubusercontent.com/hyf1888/JustLend-DAO-Doc/main/images/architecture.png)

* **Suppliers:** supply assets to the money markets of JustLend DAO smart contracts, and the assets supplied are the underlying assets.
    * Smart contracts distribute jToken that corresponds to underlying assets to users' accounts at the exchange rate.
    * Supplied assets to JustLend DAO money markets can enjoy interest earnings on their loans.Redeem: Suppliers can redeem the underlying assets they have supplied at any time.

* **Redeem:** suppliers can redeem the underlying assets they have supplied at any time.

* **Borrowers:** over-collateralize an asset can borrow from the corresponding market on JustLend DAO.
    * Unlike P2P lending, borrowers do not have to negotiate with suppliers: orders will be automatically matched by JustLend DAO smart contracts as long as the token market has sufficient liquidity.
    * Borrowing interest rates are determined by JustLend DAO smart contracts in real-time based on market supply and demand. Within a block, borrowers of the same token share the same borrowing interest rate.

* **Repay:** borrowers can repay their loans at any time.

* **Liquidation:** if the value of a borrower's collateralized assets falls below the liquidation threshold, JustLend DAO smart contracts will trigger liquidation automatically.



