# Interest Rate Model

JustLend DAO's interest rate model aims to maximize the utilization of assets while effectively managing liquidity risks. Therefore, the parameter utilization rate U of each market is particularly important, as it reflects the true situation of the available assets in each market. As the utilization rate approaches 100%, assets become scarce, making borrowing impossible.  Meanwhile, suppliers may be unable to withdraw their liquidity due to the lack of available assets. The formula of the utilization U is defined as:

<div style="text-align: center; font-size: 20px;">
    _U = Total Borrows / Total Supply_
</div>

To calibrate the interest rate model around an optimal utilization rate which reflects the real conditions, JustLend DAO provides variable interest rates for markets through two distinct interest models:

* `WhitePaperInterestRateModel:` a simple interest rate model where the borrowing rate is directly tied to the utilization rate;
* `JumpRateModelV2::` operates differently, as the interest rate jumps to a higher tier when the utilization rate surpasses a certain threshold.

### **Whitepaper Rate Model**




### **Jump Rate Model**
