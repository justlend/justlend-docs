---
title: Overview of JustLend
description: JustLend is the largest lending protocol on TRON (Compound V2 architecture) — suppliers, borrowers, jTokens, liquidation, supply mining. Entry point for the full documentation set.
---

# Overview

!!! info "Documentation freshness"
    **Protocol:** JustLend
    **Network:** TRON Mainnet
    **Markets:** 18 active + 6 legacy = 24 jToken markets ([authoritative list](../developers/apis.md#2-jtoken-address-reference)). Per-page `last-updated` is rendered in the footer (sourced from git commit history). For changelog see [CHANGELOG.md](https://github.com/justlend/justlend-docs/blob/main/CHANGELOG.md); for the machine-readable snapshot see [`/llms-full.txt`](../llms-full.txt) (header includes `last_generated` and `docs_commit`).

JustLend is a cutting-edge money market protocol powered by TRON, designed to create fund pools with interest rates determined by an algorithm based on the supply and demand of TRON assets. The protocol involves two main roles: suppliers and borrowers, who engage directly with the platform to earn or pay floating interest rates.

Each money market on JustLend represents a specific TRON asset, including TRX, TRC20 stablecoins like USDT, and other TRC20-based tokens. The platform features an open and transparent ledger that records all transactions and historical interest rates, ensuring transparency and trust among users.
<br>

### **Core Architecture of JustLend**

![architecture](https://raw.githubusercontent.com/justlend/justlend-docs/main/images/architecture.png)

* **Suppliers:** supply assets to the money markets of JustLend smart contracts, and the assets supplied are the underlying assets.
    * Smart contracts distribute jToken that corresponds to underlying assets to users' accounts at the exchange rate.
    * Supplied assets earn interest paid by borrowers in the corresponding money market.

* **Redeem:** Withdrawals are limited by the market's available liquidity and the collateral required to support the supplier's outstanding borrowings. A withdrawal must not create an account shortfall. See [Withdraw](concepts/withdraw.md) for the full conditions and steps.

* **Borrowers:** over-collateralize an asset can borrow from the corresponding market on JustLend.
    * Unlike P2P lending, borrowers do not have to negotiate with suppliers: orders will be automatically matched by JustLend smart contracts as long as the token market has sufficient liquidity.
    * Borrowing interest rates are determined by JustLend smart contracts in real-time based on market supply and demand. Within a block, borrowers of the same token share the same borrowing interest rate.

* **Repay:** borrowers can repay their loans at any time.

* **Liquidation:** If an account reaches the liquidation threshold (Risk Value > 100), the protocol allows liquidators to repay a portion of the account's debt and receive collateral as a liquidation reward.

### **Where to interact**

- **Main dApp:** <https://app.justlend.org/homeNew?lang=en-US> — supply, borrow, repay, withdraw.
- **sTRX (liquid staking):** <https://app.justlend.org/strx?lang=en-US>.
- **Energy Rental:** <https://app.justlend.org/energy?lang=en-US>.
- **Liquidation tool:** <https://app.justlend.org/liquidate?lang=en-US>.
- **Governance proposals:** <https://forum.justlend.org> (off-chain discussion) → on-chain `GovernorBravoDelegator` (see [Governance contracts](../developers/supply_and_borrow_market/governance.md)).


