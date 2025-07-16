# Interest Rate Model

JustLend DAO's interest rate model aims to maximize the utilization of assets while effectively managing liquidity risks. Therefore, the parameter utilization rate U of each market is particularly important, as it reflects the true situation of the available assets in each market. As the utilization rate approaches 100%, assets become scarce, making borrowing impossible.  Meanwhile, suppliers may be unable to withdraw their liquidity due to the lack of available assets. The formula of the utilization U is defined as:

<div style="text-align: center; font-size: 20px;">
    U = Total Borrows / Total Supply
</div>

To calibrate the interest rate model around an optimal utilization rate which reflects the real conditions, JustLend DAO provides variable interest rates for markets through two distinct interest models:

* `WhitePaperInterestRateModel:` a simple interest rate model where the borrowing rate is directly tied to the utilization rate;
* `JumpRateModelV2::` operates differently, as the interest rate jumps to a higher tier when the utilization rate surpasses a certain threshold.

## **Whitepaper Rate Model**
The Whitepaper Rate Model is straightforward, as the borrowing rate is directly proportional to the utilization. The interest rate is defined as below.

### **Borrow Rate:**
<div style="text-align: center; font-size: 20px;">
    borrow_rate(u) = a ∗ u + b
</div>

where the borrow utilization rate `u` is defined as:
<div style="text-align: center; font-size: 20px;">
    u = borrows / (cash + borrows − reserves)
</div>

* `borrows:` the total amount borrowed in the market, denominated in the underlying asset, excluding bad debts;
* `cash:` the total amount of the underlying asset held by the market at a specific time;
* `reserves:` the amount of the underlying asset held by the market that is not accessible to borrowers or suppliers, as it is reserved for purposes outlined in the protocol's tokenomics.

### **Supply Rate:**

<div style="text-align: center; font-size: 20px;">
    supply_rate(u) = borrow_rate(u) ∗ u ∗ (1 − reserve_factor)
</div>

#### **Model Parameters**
* `a:` variable interest rate slope;
* `b:` base rate per block (baseRatePerYear / blocksPerYear);
* `reserve_factor:` portion of interest income extracted from the protocol.


## **Jump Rate Model**
The Jump Rate Model is quite different with the Whitepaper Rate Model, where the interest rate jumps to a higher tier when the utilization rate exceeds U_optional
The interest rate is defined as below.

### **Borrow Rate:**

**if u < kink:**
<div style="text-align: center; font-size: 20px;">
    supply_rate(u) = a_1 * u + b
</div>

**if u >= kink:**

<div style="text-align: center; font-size: 20px;">
    supply_rate(u) = a_1 * kink + a_2 * (u - kink) + b
</div>

where the borrow utilization rate `u` is defined as:
<div style="text-align: center; font-size: 20px;">
    u = borrows / (cash + borrows − reserves)
</div>

* `borrows:` the total amount borrowed in the market, denominated in the underlying asset, excluding bad debts.
* `cash:` the total amount of the underlying asset held by the market at a specific time.
* `reserves:` the amount of the underlying asset held by the market that is not accessible to borrowers or suppliers, as it is reserved for purposes outlined in the protocol's tokenomics.

### **Supply Rate:**

<div style="text-align: center; font-size: 20px;">
    supply_rate(u) = borrow_rate(u) ∗ u ∗ (1 − reserve_factor)
</div>

#### **Model Parameters**
* `a_1:` variable interest rate slope1;
* `a_2:` variable interest rate slope2;
* `b:` base rate per block (baseRatePerYear / blocksPerYear);
* `kink:` the utilization point at which the jump multiplier is applied, and the variable interest rate slope shifts from slope1 to slope2;
* `reserve_factor:` portion of interest income extracted from the protocol.
