JustLend DAO SBM V2 is a fully upgraded decentralized lending protocol built on the TRON network. The SBM V2 adopts an **isolated-collateral lending protocol** with a dual-layer structure of **Vaults** and **Markets**, and introduces the Adaptive Curve Interest Rate Model. This new design aims to provide higher capital efficiency for depositors and borrowers while ensuring a robust risk isolation framework.

## Protocol Architecture

### Vaults
* A Vault serves as the liquidity aggregation and distribution hub. Depositors can supply a single type of asset (such as USDT or USDD) into its corresponding Vault;
* The Vault allocates these deposits across multiple Markets, each backed by a specific collateral asset;
* In return, depositors earn yield from all underlying markets, with interest weighted and distributed automatically according to each market’s performance.

### Markets
* Each Market represents an independent lending environment. A Market supports only one type of collateral and is linked to a specific Vault (e.g., USDT Vault).
* Borrowers use the supported collateral to borrow assets from the linked Vault;
* Every Market is isolated, the risk associated with one collateral type will not affect others, effectively preventing cross-asset contagion.

### Roles and Mechanisms

* **Depositors (Suppliers)**
    * Supply a single depositable asset (e.g., USDT) into the corresponding Vault;
    * The Vault aggregates liquidity from all suppliers of the same asset;
    * Depositors indirectly lend assets to multiple Markets and receive interest weighted by each Market’s performance.

* **Borrowers**
    * Pledge supported collateral assets to borrow funds from the Market;
    * Borrowing activities are confined within individual Markets;
    * Interest paid by borrowers flows back into the Vault and is distributed proportionally among depositors.


## Interest Rate Model
JustLend DAO SBM V2 introduces the **Adaptive Curve Interest Rate Model**. It builds upon the Jump Curve model used in SBM V1, but adds **dynamic adaptability**, allowing real-time rate adjustments to keep market utilization near an optimal level. This design ensures both rate stability and maximum capital efficiency.

Just Like SBM V1, SBM V2 uses a **jump-style rate curve**, where the borrow rate rises sharply once utilization exceeds the kink point. However, V2 introduces a dynamic vertical shift:

* When utilization is low → the entire curve shifts downward, lowering borrow rates to stimulate borrowing;
* When utilization is high → the curve shifts upward, raising rates to encourage repayments.

### Key Concepts

**Target Utilization**

The Target Utilization represents the equilibrium point of the Interest Rate Model’s Jump Curve. It reflects the optimal balance between borrowed assets and available liquidity, calculated as:

    Utilization = BorrowedAssets / (BorrowedAssets + AvailableLiquidity)
                                                            
When the utilization level reaches the target, the market is considered stable, meaning borrowing and liquidity levels are appropriately balanced.

**Rate at Target**

The Rate at Target defines the borrowing interest rate when utilization equals the target. It is initially configured by the protocol (for example, at 4% annualized) and is dynamically adjusted over time based on market conditions. Each market maintains its own rateAtTarget parameter, allowing for fine-grained control and independent optimization across different markets.

**Adaptive Mechanism**

To maintain stability, the Interest Rate Model includes an Adaptive Mechanism. When the actual utilization deviates significantly from the target for a prolonged period, the system automatically adjusts the entire interest rate curve at a controlled rate.
* If utilization < target → **rateAtTarget** decreases to encourage borrowing.
* If utilization > target → **rateAtTarget** increases to promote repayments.

This adaptive mechanism, driven by target utilization and time, enables the protocol to continuously self-regulate utilization levels, ensuring market efficiency and sustainability without the need for governance intervention.

## Liquidations
The core liquidation logic of the SBM V2 protocol remains consistent with the mechanism used in SBM V1. A borrower becomes eligible for liquidation when the value of their debt exceeds the value of their collateral adjusted by the Collateral Factor (CF). This condition is evaluated using the **Liquidation Loan-to-Value (LLTV) threshold**, which varies by market based on the underlying collateral asset.

Under V2, liquidation is triggered when LTV equals the market’s defined LLTV (e.g., 80%).

    LTV = (Borrow Amount * Borrow Price) / (Collateral Amount * Collateral Price) ​
                                                          
This is equivalent to the SBM V1 risk metric, a position becomes liquidatable once the Risk Level equals to 100%:

    Risk Level = Total Borrow / Borrow Limit * 100 = Total Borrow / ∑ (Asset supplied * Collateral Factor)
                                                          
However, unlike V1, SBM V2 introduces a significant improvement through its isolated-lending model, where each market operates independently with its own risk parameters (e.g., LLTV.). This architecture ensures that risk events are contained within individual markets, preventing unwanted spillover effects and reducing systemic liquidation risk across the protocol. As a result, users benefit from enhanced safety, more predictable outcomes, and a more robust overall risk framework.


##  Comparison: JustLend SBM V1 vs V2
To provide a clearer understanding of the improvements and optimizations introduced in JustLend DAO SBM V2, the following table presents a detailed comparison with V1. This comparison highlights the key differences in design, functionality, and performance, allowing users to quickly grasp the core enhancements made in the latest version.

| Aspect | SBM V1 | SBM V2 |
|:------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|-------|
| **Market Structure**          | Cross-Collateral Market: Multiple assets can be used as collateral and borrowed against each other.                                              | Isolated Markets: 1-to-1 asset mapping; each market only supports one collateral and one borrowable asset. |
| **Lending Flexibility**       | Users can use any asset in their portfolio as collateral and borrow any supported asset. A unified large market allows cross-collateral lending. | Single market: Only one collateral type can be used to borrow a specific asset. Multiple markets are used to enable lending of different assets. |
| **Risk Isolation**            | Risks are shared across assets, with collateral automatically used as borrowed assets.                                                           | Each market is independent, with complete risk isolation. |
| **Liquidity Characteristics** | Shared liquidity across assets and larger liquidity pools; collateral can also be borrowed.                                                      | Independent liquidity for each asset pair, which may lead to fragmented liquidity; collateral cannot be borrowed. |
| **User Investment Method**    | Users deposit assets directly into JustLend’s market.                                                                                            | Users deposit assets into a Vault, and the Vault Manager is responsible for maximizing investment returns. |
| **User Investment Yield**     | Users can only invest their assets into one market at a time.                                                                                    | Vault Managers adjust investments every hour, optimizing returns across multiple markets. |
| **Borrower’s Collateral**     | Borrower’s collateral and user investments are mixed, and collateral can be borrowed as well.                                                    | User investments and borrower’s collateral are separated, and collateral cannot be borrowed again. |
| **Collateral Interest**       | Collateral shares deposit interest, which dilutes deposit APY.                                                                                   | Borrower’s collateral does not earn interest, ensuring investor returns are not diluted. |

According to the above comparison, we can see the JustLend DAO SBM V1 is ideal for users and institutions seeking simplified lending operations and shared liquidity. Its cross-collateralized market allows multiple assets to interact freely, enabling users to supply and borrow across a unified liquidity pool. This design offers high capital efficiency and ease of use, making it suitable for users with diversified portfolios who prefer flexibility and simplicity over strict risk isolation.

In contrast, JustLend DAO SBM V2 introduces a more advanced and modular structure featuring Vaults and Isolated Markets, designed for users who prioritize risk control, optimized yields, and strategic asset management. Each market operates independently, ensuring that the risks of one collateral asset do not affect others. Through Vault Managers, deposits are dynamically allocated to maximize returns across multiple markets. This makes SBM V2 particularly suitable for professional users, DeFi strategists, and institutions seeking higher yield efficiency, customizable risk exposure, and fine-grained control over investment strategies.

