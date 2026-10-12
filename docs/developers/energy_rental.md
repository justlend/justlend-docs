---
title: Energy Rental — contract reference
description: JustLend DAO EnergyRental contract reference — rentResource, returnResource, returnResourceByReceiver, liquidate, getRentInfo, plus TronWeb examples. Powers the one-to-many TRON Energy marketplace.
---

# Energy Rental

!!! info "About this page"
    * **Protocol:** JustLend DAO Energy Rental (one-to-many TRON Energy marketplace)
    * **Network:** TRON Mainnet
    * **Contract:** [`TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd`](https://tronscan.org/#/contract/TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd)
    * **Units:** contract `amount` parameters refer to **delegated TRX in sun** (1 TRX = 10^6 sun), **not** energy units. Divide target energy by `energyStakePerTrx` to obtain whole TRX, then convert to sun before a contract call.
    * **`resourceType`:** `0 = bandwidth`, `1 = energy`.
    * **Constraint:** receiver must be a regular account, not a contract.
    * **User-side overview:** [Energy Rental concept](../getting_started/concepts/energy_rental.md) 
    * **ABI:** [`abis/energy-market.json`](abis/energy-market.json), rate model in [`abis/energy-rate-model.json`](abis/energy-rate-model.json).


All transactions on JustLend DAO require Energy, which can only be acquired through staking or burning TRX. This process involves high costs and lengthy procedures. In response, JustLend DAO introduces the Energy Rental service, allowing users to rent Energy at a significantly reduced price compared to staking or burning TRX.
The contract [EnergyRental](https://tronscan.org/#/contract/TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd) used to set up the Energy Rental service.


### **PrePay & Refund**

During the energy rental process, a prepayment amount, which includes a deposit and rent, is calculated based
on the **Rental Amount** and **Rental Duration**. The detailed formula is as follows:

<div style="text-align: center; font-size: 20px;">
    PrepaySun = ceil(amountSun × max(rentalRateMantissa, stableRateMantissa) × (durationSeconds + 86400 + liquidateThresholdSeconds) / 10^18) + feeSun
</div>

This is a **budget estimate for a new rental**, not an executable quote or a guaranteed upper bound after rates change. Renewals also depend on the existing order and remaining deposit. Upon termination, the refundable amount depends on actual usage, rates, and contract settlement; the following historical illustration must not be treated as a guaranteed minimum refund:

<div style="text-align: center; font-size: 20px;">
    Illustrative reserve = trxAmount × max(rentalRateMantissa, stableRateMantissa) / 10^18 × (21600 + liquidateThresholdSeconds) + feeTrx
</div>

#### **Parameters:**

* To determine the value of `trxAmount`, use the following formula:
    * `energyAmount:` is the amount of energy you are renting **(Rental Amount)**.
    * `energyStakePerTrx:` is the energy staked per TRX, derived from the [/lend/strx](https://openapi.just.network/lend/strx) API as `10000 / rentInfo.priceFor10KEnergByStake`.

<div style="text-align: center; font-size: 20px;">
    trxAmount = energyAmount / energyStakePerTrx
</div>

* `durationSeconds:` the duration of the energy rental in seconds, calculated by converting the **Rental Duration** into seconds.
* `rentalRateMantissa:` current per-second rate from `_rentalRate(amountSun, resourceType)`, scaled by 10^18.
* `stableRateMantissa:` smoothed rate from `_stableRate(resourceType)`, scaled by 10^18. Use the higher of these two rates, not just the current rental rate.
* `liquidateThresholdSeconds:` additional time reserve from `liquidateThreshold()`, in seconds. Do not assume it is zero.
* `feeSun:` liquidation fee reserve, estimated as `max(minFee(), ceil(amountSun × feeRatio() / 10^18))`. `minFee()` is in sun and `feeRatio()` is a 10^18-scaled ratio. A fixed 20 TRX is not a substitute for the current minimum and proportional fee; the latter can be larger.

**Note:** read all parameters from the [EnergyRental](https://tronscan.org/#/contract/TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd) contract on the same network and at a consistent state. These are the inputs used by the [MCP rental estimator](https://github.com/justlend/mcp-server-justlend/blob/7d53a6ca755fbe70724ae6aaed9276462716cee2/src/core/services/energy-rental.ts). Missing reads must stop the estimate; do not silently replace them with historical constants. Re-quote before a separately confirmed transaction.



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
* **Returns:** the recorded total rental income, in sun (`1 TRX = 1,000,000 sun`).


### Cumulative claimed rental income

```solidity
function rentClaimed() external view returns (uint256)
```

* **Parameter description:** N/A.
* **Returns:** the cumulative rental income already transferred from the market to sTRX, in **sun** (`1 TRX = 1,000,000 sun`). This is the recorded cumulative counter, not the amount claimable now.

`totalRent()` is a different accounting value and must not be reused as cumulative claimed income. The similarly named `claimRental()` is a state-changing collection operation, not a historical read; see [Protocol income collection](#protocol-income-collection). The read methods, collection method, and `RentClaimed` event are included in [`energy-market.json`](abis/energy-market.json).


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

### Protocol income collection

```solidity
function claimRental() external returns (uint256)
```

This is the protocol's rental-income collection path, **not a user-facing query for cumulative claimed rent**. It is not `view` and must not appear in a read-only monitoring workflow.

* **Parameters:** none.
* **Caller:** only the sTRX contract configured by the market's `strx()` getter; ordinary user wallets cannot call it successfully.
* **Returns:** the rental amount actually transferred into sTRX **by this call**, in **sun** (`1 TRX = 1,000,000 sun`). It is **not** an all-time total. The transfer is capped by the market's available TRX balance; if nothing is transferred, the return is `0`.
* **Accounting event:** a positive transfer increments `rentClaimed` and emits `RentClaimed(uint256 add, uint256 totalClaimed)`. Both values are in sun: `add` is this transfer and `totalClaimed` is the cumulative value after it. Both fields are non-indexed. A zero transfer emits no `RentClaimed` event.

These semantics were checked against the current Mainnet `MarketG1` implementation (`TNoHbPuBQrVanVf9qxUsSvHdB2eDkeDAKD`): compiler output matches its executable bytecode with only compiler metadata excluded. A successful Mainnet settlement receipt also matches the event amount and the internal TRX transfer to sTRX. See [ABI scope and provenance](abis/index.md#scope-and-provenance). No user transaction example is provided.

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
    * `msg.sender:` resource payer.
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
  // GET https://openapi.just.network/lend/strx → rentInfo.priceFor10KEnergByStake
  const res = await fetch('https://openapi.just.network/lend/strx');
  const { data } = await res.json();
  // energy staked per 1 TRX = 10000 / (TRX to self-stake for 10k energy)
  const energyPerTrx = 10000 / Number(data.rentInfo.priceFor10KEnergByStake);
  const trxNeeded    = targetEnergy / energyPerTrx;    // in TRX
  return BigInt(Math.ceil(trxNeeded * 1_000_000));     // sun
}
```

### 2. Estimate the full new-rental prepayment (read-only)

The pure helper below uses integer raw units, both rates, the additional time threshold, and a dynamic fee. Pass current contract values as integer strings or `BigInt` values. It does **not** sign or broadcast a transaction and does not account for an existing rental.

```javascript
function estimatePrepaymentSun({ amountSun, rentalRateMantissa, stableRateMantissa,
  durationSeconds, liquidateThresholdSeconds, feeRatioMantissa, minFeeSun }) {
  const raw = [amountSun, rentalRateMantissa, stableRateMantissa, durationSeconds,
    liquidateThresholdSeconds, feeRatioMantissa, minFeeSun];
  if (raw.some(value => !['string', 'bigint'].includes(typeof value) ||
    !/^\d+$/.test(String(value)))) throw new Error('Use non-negative integer raw values');
  const [amount, rental, stable, duration, threshold, feeRatio, minFee] = raw.map(BigInt);
  if (amount === 0n || duration === 0n) throw new Error('New rentals need positive amount and duration');
  const scale = 10n ** 18n;
  const ceilScaled = value => (value + scale - 1n) / scale;
  const rate = rental > stable ? rental : stable;
  const proportionalFee = ceilScaled(amount * feeRatio);
  const fee = proportionalFee > minFee ? proportionalFee : minFee;
  return ceilScaled(amount * rate * (duration + 86_400n + threshold)) + fee;
}
```

Illustrative controls (not current prices): with 100 TRX delegated, a 1-day duration, rental rate `1e12`, stable rate `2e12`, a 3,600-second threshold, fee ratio `8e13`, and minimum fee 20 TRX, the estimate is **55.28 TRX**. With 1,000,000 TRX delegated, the same rates and fee ratio, and a zero threshold, the proportional fee is **80 TRX**, not 20, and the estimate is **345,680 TRX**.

For a current read-only MCP estimate, call `calculate_energy_rental_price` with `{"energyAmount":300000,"durationHours":24,"network":"mainnet"}`. For a renewal, provide `receiverAddress` and use the tool's existing-order calculation instead. Inspect the result and stop on stale/missing data. Only a separate, explicitly confirmed `rent_energy` operation or `rentResource(receiver, amountSun, 1)` transaction should sign and broadcast, with reviewed prepayment supplied as `callValue`. Estimation itself must never trigger that write.

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
