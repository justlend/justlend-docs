# Energy Rental

All transactions on JustLend DAO require Energy, which can only be acquired through staking or burning TRX. This process involves high costs and lengthy procedures. In response, JustLend DAO introduces the Energy Rental service, allowing users to rent Energy at a significantly reduced price compared to staking or burning TRX.
The contract [EnergyRental](https://tronscan.io/#/contract/TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd) used to set up the Energy Rental service.


### **PrePay & Refund**

During the energy rental process, a prepayment amount, which includes a deposit and rent, is calculated based
on the **Rental Amount** and **Rental Duration**. The detailed formula is as follows:

<div style="text-align: center; font-size: 20px;">
    Prepay = trxAmount ∗ max(rentalRate, stableRate) ∗ (durationValueInSeconds + 86400 + liquidateThreshold) + fee
</div>

Upon normal termination of the rental, a portion of the deposit will be refunded based on the energy usage. The specific refund calculation formula is as follows:

<div style="text-align: center; font-size: 20px;">
    Refund at least = trxAmount ∗ max(rentalRate, stableRate) ∗ (21600 + liquidateThreshold) + fee
</div>

#### **Parameters:**

* To determine the value of `trxAmount`, use the following formula:
    * `energyAmount:` is the amount of energy you are renting **(Rental Amount)**.
    * `energyStakePerTrx:` is the energy staked per in Trx, which can be retrieved by calling the [/strx/dashboard](https://labc.ablesdxd.link/strx/dashboard) API.

<div style="text-align: center; font-size: 20px;">
    trxAmount = energyAmount / energyStakePerTrx
</div>

* `durationValueInSeconds:` the duration of the energy rental in seconds, calculated by converting the **Rental Duration** into seconds.
* `rentalRate:` the borrowing interest rate, which is the rate paid per second by the borrower to the staker, scaled by 10^18.
* `stableRate:` the weighted average interest rate for borrowings, which is a constantly updating six-hour rolling average, scaled by 10^18.
* `liquidateThreshold:` the liquidation threshold, which is the remaining rental duration of the user's prepayment, initialized to 0.
* `fee:` the penalty reserve for liquidation. Users who execute liquidation can receive a liquidation reward calculated as `Max(40 TRX, 0.05% * energyAmount / energyRentPerTrx)`, which can be retrieved by calling the [/strx/dashboard](https://labc.ablesdxd.link/strx/dashboard) API. The minimum fee is 40 TRX.

**Note:** the parameters of `rentalRate`, `stableRate` and `liquidateThreshold` can be obtained by calling the [EnergyRental](https://tronscan.io/#/contract/TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd) contract.



## **Query Interface**

### **Rental Order Information**
View the information of a rental order.
``` solidity
function rentals (address renter, address receiver, uint256 resourceType) public view returns (RentalInfo)

struct RentalInfo {
    uint256 amount;
    uint256 securityDeposit;
    uint256 rentIndex;
}
```

* **Parameter description:**
    * `renter:` order payer;
    * `receiver:` the resource receiver of this rental;
    * `resourceType:` resource type, 0: bandwidth; 1: energy.
* **Returns:**
    * `amount:` order resources corresponding to the amount of TRX  (delegated TRX amount);
    * `securityDeposit:` order deposit, not updated to current;
    * `rentIndex:` order's global index at the time of its last update.


### **Current Rental Order Information (updated to current)**
View the information of an rental order, with the returned data updated to current.
``` solidity
function getRentInfo (address renter, address receiver, uint256 resourceType) external view returns (uint256, uint256)
```

* **Parameter description:**
    * `renter:` order payer;
    * `receiver:` the resource receiver of this rental;
    * `resourceType:` resource type, 0: bandwidth; 1: energy.
* **Returns:**
    * `securityDeposit:` order deposit, updated to current；
    * `rentIndex:` eal-time global index of the order at the time of query.


### **Bad Debt**
If the user's rent is greater than securityDeposit, a bad debt will be generated. This field will be updated when repayment or liquidation occurs.
``` solidity
function badDebt() view external returns (uint256)
```

* **Parameter description:** N/A;
* **Returns:** the amount of bad debt in TRX, minimum unit.


### **Covered Bad Debt**
Bad debts will be filled when the collectible rewards (`_settleIncome`) are updated or the `repayBadDebt` function is triggered.
``` solidity
function badDebtCovered() view external returns (uint256)
```

* **Parameter description:** N/A;
* **Returns:** the amount of cumulative bad debt has been filled in TRX , minimum unit.


### **Bad Debt To Be Covered**
The amount of bad debt that has not been processed. In fact, this value is equal to  the amount of badDebt minus badDebtCovered.
``` solidity
function badDebtGap() view external returns (uint256)
```

* **Parameter description:** N/A;
* **Returns:** the amount of bad debt to be covered in TRX, minimum unit.


### **Total Rent Income**
Rental income from renting energy.
``` solidity
function totalRent() view external returns (uint256)
```

* **Parameter description:** N/A;
* **Returns:** the amount of total rental income.


### **Claimed Rent Income**
The STRX contract can extract the income through the `claimRental` function, which records the accumulated income that has been extracted.
``` solidity
function totalRent() view external returns (uint256)
```

* **Parameter description:** N/A;
* **Returns:** the amount of accumulate income that has been extracted.


### **Liquidation Rate**
The `liquidateRate` is used during liquidation. If the price fluctuates greatly, it will be diluted for 6 hours. Rapidly raised prices will not take effect immediately during the liquidation process.
``` solidity
function _liquidateRate(uint256 resourceType) view external returns (uint256)
```

* **Parameter description:**
    * `resourceType:` resource type, 0: bandwidth; 1: energy.
* **Returns:** current liquidation rate.


### **Rental Rate**
Get the latest rental rate. when the amount is passed as 0, it returns the current tental rate. When the amount is greater than 0, for example, 100, it returns the rental rate after the energy changes by 100.
``` solidity
function _rentalRate(uint256 amount, uint256 resourceType) view external returns (uint256)
```

* **Parameter description:**
    * `amount:` order resources corresponding to the amount of TRX;
    * `resourceType:` resource type, 0: bandwidth; 1: energy.
* **Returns:** current rental rate.



## **Write Interface**

### **Rent Resources**
Rent resources, allow amount = 0 (extension only) or msg.value = 0 (no new deposit), both are 0 is not allowed.
``` solidity
function rentResource (address receiver, uint256 amount, uint256 resourceType) external payable
```

* **Parameter description:**
    * `receiver:` the resource receiver of this rental. Not allowed to be a contract or an unactivated account;
    * `amount:` the rent resource corresponding to the amount of TRX (**delegated TRX amount**), the minimum unit, if the amount is not 0 (renewal only), it must be greater than 1 TRX;
    * `resourceType:` resource type, 0: bandwidth; 1: energy;
    * `msg.sender:` the payer for this rental;
    * `msg.value:` new deposit of this time.
* **Returns:** None, revert on failure.

#### **Event**
``` solidity
RentResource (address indexed renter, address indexed receiver, uint256 addedAmount, uint256 resourceType, uint256 addedSecurityDeposit, uint256 amount)
```

* Emits when renting occurs.
    * `renter:` order payer;
    * `receiver:` the resource receiver of this rental;
    * `addedAmount:` the TRX amount (minimum unit) of the newly-rent resource;
    * `resourceType:` resource type, 0: bandwidth; 1: energy;
    * `addedSecurityDeposit:` the added deposit amount;
    * `amount:` the total amount of rental resources in the order after renting.


### **Return Resources (called by payer)**
Return resources. Return resources in the order (msg.sender, receiver, resourceType). When the remaining deposit is insufficient, all resources will be forcibly emptied, and the remaining deposit will be returned to the order payer.
``` solidity
function returnResource (address receiver, uint256 amount, uint256 resourceType) external returns (uint256)
```

* **Parameter description:**
    * `receiver:` the resource receiver of this rental;
    * `amount:` rent resource corresponding to the amount of TRX  (**delegated TRX amount**), the minimum unit;
    * `resourceType:` resource type, 0: bandwidth; 1: energy;
    * `msg.sender:` resource receiver.
* **Returns:** the amount of the deposit returned in this operation. 0 for a partial return.

#### **Event**
``` solidity
ReturnResource( address indexed renter, address indexed receiver, uint256 subedAmount, uint256 resourceType, uint256 usageRental, uint256 subedSecurityDeposit, uint256 amount)
```

* Emits when renting occurs.
    * `renter:` order payer;
    * `receiver:` the resource receiver of this rental;
    * `subedAmount:` the amount of TRX (minimum unit) for returned resources;
    * `resourceType:` resource type, 0: bandwidth; 1: energy;
    * `usageRental:` the cost of recovery for the used resources in the returned resources;
    * `subedSecurityDeposit:` the refunded deposit amount (0 for partial returns);
    * `amount:` the remaining amount of rental resources after returning resources.


### **Return resources (called by receiver)**
Return resources. Return resources in the order (renter, msg.sender, resourceType). When the remaining deposit is insufficient, all resources will be forcibly emptied, and the remaining deposit will be returned to the order payer.
``` solidity
function returnResourceByReceiver (address renter, uint256 amount, uint256 resourceType) external returns (uint256)
```

* **Parameter description:**
    * `renter:` order payer;
    * `amount:` rent resource corresponding to the amount of TRX  (**delegated TRX amount**), the minimum unit;
    * `resourceType:` resource type, 0: bandwidth; 1: energy;
    * `msg.sender:` resource receiver.
* **Returns:** the amount of the deposit returned in this operation. 0 for partial return.


### **Liquidate**
When the order deposit is insufficient, the liquidator can liquidate the order, and the liquidator will get the liquidation reward. If there is any remaining deposit, it will be returned to the order payer.
``` solidity
function liquidate (address renter, address receiver, uint256 resourceType) external returns (uint256)
```

* **Parameter description:**
    * `renter:` order payer;
    * `receiver:` the resource receiver of this rental;
    * `resourceType:` resource type, 0: bandwidth; 1: energy;
    * `msg.sender:` liquidator.
* **Returns:** Liquidation reward in this operation.

#### **Event**
``` solidity
Liquidate( address indexed liquidator, address indexed renter, address indexed receiver, uint256 amount, uint256 resourceType, uint256 usageRental, uint256 liquidateFee, uint256 sendBack)
```

* Emits when liquidation occurs.
    * `liquidator:` the person liquidate the order;
    * `renter:` order payer;
    * `receiver:` the resource receiver of this rental;
    * `amount:` rent resource corresponding to the amount of TRX  (**delegated TRX amount**), the minimum unit;
    * `resourceType:` resource type, 0: bandwidth; 1: energy;
    * `usageRental:` the fee for the recovery time of the order resource usage;
    * `liquidateFee:` the liquidation reward received by the liquidator;
    * `sendBack:` the remaining deposit received by the payer.
