---
title: Energy Rental — contract reference
description: JustLend DAO EnergyRental contract reference — rentResource, returnResource, returnResourceByReceiver, liquidate, getRentInfo, plus TronWeb examples. Powers the one-to-many TRON Energy marketplace.
---

# Energy Rental

!!! info "About this page"
    **Protocol:** JustLend DAO Energy Rental (one-to-many TRON Energy marketplace) · **Network:** TRON Mainnet · **Contract:** [`TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd`](https://tronscan.org/#/contract/TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd) (immutable) · **Units:** `amount` parameters refer to the **delegated TRX amount in sun** (1 TRX = 10⁶ sun), **not** the energy amount — divide your target energy by `energyStakePerTrx` from the dashboard API to get TRX. · **`resourceType`:** `0 = bandwidth`, `1 = energy`. · **Constraint:** receiver must be a regular account, not a contract. · **User-side overview:** [Energy Rental concept](../getting_started/concepts/energy_rental.md) · **ABI:** [`abis/energy-market.json`](abis/energy-market.json), rate model in [`abis/energy-rate-model.json`](abis/energy-rate-model.json).

All transactions on JustLend DAO require Energy, which can only be acquired through staking or burning TRX. This process involves high costs and lengthy procedures. In response, JustLend DAO introduces the Energy Rental service, allowing users to rent Energy at a significantly reduced price compared to staking or burning TRX.
The contract [EnergyRental](https://tronscan.org/#/contract/TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd) used to set up the Energy Rental service.


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
* `fee:` the penalty reserve for liquidation. Users who execute liquidation can receive a liquidation reward calculated as `Max(20 TRX, 0.01% * energyAmount / energyRentPerTrx)`, which can be retrieved by calling the [/strx/dashboard](https://labc.ablesdxd.link/strx/dashboard) API. The minimum fee is 20 TRX.

**Note:** the parameters of `rentalRate`, `stableRate` and `liquidateThreshold` can be obtained by calling the [EnergyRental](https://tronscan.org/#/contract/TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd) contract.



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


<a id="rental-rate"></a>

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

<a id="rent-resources"></a>

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


<a id="return-resources-called-by-payer"></a>

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


<a id="return-resources-called-by-receiver"></a>

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


<a id="examples-tronweb"></a>

## **Examples (TronWeb)**

```javascript
const TronWeb = require('tronweb');
const tronWeb = new TronWeb({
  fullHost: 'https://api.trongrid.io',
  headers: { 'TRON-PRO-API-KEY': process.env.TRONGRID_API_KEY },
  privateKey: process.env.PRIVATE_KEY,
});

const ENERGY_RENTAL = 'TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd'; // TRON Mainnet
const ENERGY = 1;     // resourceType for energy
// const BANDWIDTH = 0; // resourceType for bandwidth
```

### 1. Convert "I want N energy" → required delegated TRX

The contract takes **delegated TRX in sun**, not energy units. First query the current ratio:

```javascript
async function energyToDelegatedSun(targetEnergy) {
  // GET https://openapi.just.network/strx/dashboard → energyStakePerTrx
  const res = await fetch('https://openapi.just.network/strx/dashboard');
  const { data } = await res.json();
  const energyPerTrx = Number(data.energyStakePerTrx); // energy per 1 TRX
  const trxNeeded    = targetEnergy / energyPerTrx;    // in TRX
  return BigInt(Math.ceil(trxNeeded * 1_000_000));     // sun
}
```

### 2. Rent energy (the `rentResource` call)

```javascript
async function rentEnergy({ receiver, targetEnergy, durationSeconds }) {
  const rental = await tronWeb.contract().at(ENERGY_RENTAL);

  // Compute prepayment off-chain (formula from the page above):
  //   prepay = trxAmount × max(rentalRate, stableRate) × (duration + 86400 + liquidateThreshold) + fee
  // Easiest: query `_rentalRate(amount, resourceType)` for the current per-second rate
  //   and the EnergyRental dashboard for `stableRate`, `liquidateThreshold`, and `fee`.
  // Simplest path: overshoot the prepayment slightly; the unused portion is refunded on return.

  const amountSun = await energyToDelegatedSun(targetEnergy);
  const rentalRate = BigInt((await rental._rentalRate(amountSun, ENERGY).call()).toString());

  // Rough prepayment (use a conservative buffer; precise formula in the page above)
  const buffer = BigInt(durationSeconds + 86_400);
  const fee    = 20_000_000n; // 20 TRX minimum liquidation reserve
  const prepay = amountSun * rentalRate * buffer / (10n ** 18n) + fee;

  const txId = await rental
    .rentResource(receiver, amountSun.toString(), ENERGY)
    .send({ callValue: Number(prepay), feeLimit: 200_000_000 });

  console.log('rent tx:', txId);
}
```

!!! tip
    For prepayment precision, use the JustLend MCP server's `calculate_energy_rental_price` tool — it implements the full formula and accounts for `stableRate` and `liquidateThreshold`. See [MCP Server](../ai_support/mcp_server.md).

### 3. Return rental & reclaim deposit

```javascript
async function returnEnergy({ receiver, returnAmountSun }) {
  const rental = await tronWeb.contract().at(ENERGY_RENTAL);

  // Called by the *payer* (renter)
  const txId = await rental
    .returnResource(receiver, returnAmountSun, ENERGY)
    .send({ feeLimit: 200_000_000 });
  console.log('return tx:', txId);
}

// If called by the receiver of the rented energy:
async function returnByReceiver({ renter, returnAmountSun }) {
  const rental = await tronWeb.contract().at(ENERGY_RENTAL);
  return rental
    .returnResourceByReceiver(renter, returnAmountSun, ENERGY)
    .send({ feeLimit: 200_000_000 });
}
```

### 4. Query an active rental

```javascript
async function getRental({ renter, receiver }) {
  const rental = await tronWeb.contract().at(ENERGY_RENTAL);
  // Real-time view (updated to current block)
  const [securityDeposit, rentIndex] = await rental
    .getRentInfo(renter, receiver, ENERGY).call();
  return { securityDeposit: securityDeposit.toString(), rentIndex: rentIndex.toString() };
}
```
