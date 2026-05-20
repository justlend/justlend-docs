# Staked TRX

!!! info "Network & precision"
    The contract address below is **TRON Mainnet**. TRX amounts are in **sun** (1 TRX = 10⁶ sun). sTRX is an 18-decimal TRC20. The `exchangeRate()` is scaled by `1e18`.

Based on Stake 2.0, with TRX Liquid Staking, users can stake TRX to get sTRX tokens and gain high rewards. Compared to traditional staking, TRX Liquid Staking is easier to use and more profitable. Staked TRX will be used automatically for voting and governance, and gain rewards via Energy Rental.
The contract [StakedTRX](https://tronscan.org/#/token20/TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5) used to set up the staked TRX service.


## **Query Interface**

<a id="exchange-rate"></a>

### **Exchange Rate**
Query the exchange rate between sTRX and TRX.
``` solidity
function exchangeRate() public view returns (uint256)
```

* **Parameter description:** N/A.
* **Returns:** exchange rate, 1 sTRX / 1 TRX exchange rate, scaled by 1e18.


### **Total TRX Assets**
Query the total TRX assets managed by contract.
``` solidity
function totalUnderlying() public view returns (uint256)
```

* **Parameter description:** N/A.
* **Returns:** the total assets of TRX managed by contract, the minimum unit.


### **User Balance in TRX**
Query the amount of TRX corresponding to the sTRX held by user.
``` solidity
function balanceInTrx(address _account) public view returns (uint256)
```

* **Parameter description:**
    *  `_account:` the user address.
* **Returns:** the amount of TRX corresponding to the sTRX held by user, the minimum unit.


### **Current Unfreezing Round**
Query the current unfreezing round of the contract. The initial value is 1.
``` solidity
function round() view external returns (uint256)
```

* **Parameter description:** N/A.
* **Returns:** current unfreezing round.


### **Claimable Amount in TRX**
The amount of TRX that can be withdrawn after the unfreezing period has expired.
``` solidity
function claimable() external returns (uint256)
```

* **Parameter description:** N/A.
* **Returns:** the amount of TRX that can be claimed.


### **Withdrawal Amount in TRX**
The amount of TRX being withdrawn. This value is increased when the user withdraws.
``` solidity
function withdrawal() external returns (uint256)
```

* **Parameter description:** N/A.
* **Returns:** the amount of TRX being withdrawn.


### **Unfreeze Balance in TRX**
The total amount to be unfrozen. If the user withdraws but has not completed the round, it will enter the unfreezing queue.
``` solidity
function balanceToUnfreeze() external returns (uint256)
```

* **Parameter description:** N/A.
* **Returns:** the amount of TRX to be unfrozen, minimum unit.


### **Freeze Balance in TRX**
The amount to be frozen. As long as the value is greater than 1 TRX, the freezing operation will be performed.
``` solidity
function balanceToFreeze() external returns (uint256)
```

* **Parameter description:** N/A.
* **Returns:** the amount of TRX to be frozen, minimum unit.



## **Write Interface**

<a id="deposit-trx"></a>

### **Deposit TRX**
Deposit TRX assets and receive sTRX.
``` solidity
function deposit() external payable returns (uint256)
```

* **Parameter description:**
    * `msg.value:` the amount of TRX to deposit.
* **Returns:** the amount of sTRX received by user through exchange, the minimum unit.

#### **Event**
``` solidity
Deposit(address user, uint256 trxAmount, uint256 strx, uint256 userHoldStrx)
```

* Emits when user successfully deposits TRX.
    * `trxAmount:` the amount of TRX user deposits;
    * `strx:` the amount of sTRX user gets;
    * `userHoldStrx:` the total amount of sTRX held by user after the deposit.


<a id="withdraw-strx"></a>

### **Withdraw sTRX**
Specify the amount of sTRX to withdraw, the minimum unit.
``` solidity
function withdraw(uint256 tokenAmount) external returns (uint256)
```

* **Parameter description:**
    * `tokenAmount:` the amount of sTRX to withdraw.
* **Returns:** the amount of TRX to be unfrozen when user withdraws, the minimum unit.

#### **Event**
``` solidity
Withdraw(address user, uint256 strx, uint256 trxAmount, uint256 userHoldStrx)
```

* Emits when user successfully withdraws sTRX.
    * `strx:` the amount of sTRX user withdraws;
    * `trxAmount:` the amount of TRX user gets;
    * `userHoldStrx:` the total amount of sTRX held by user after the withdrawal.


<a id="withdraw-strx-with-the-amount-of-trx-specified"></a>

### **Withdraw sTRX (with the amount of TRX specified)**
Specify the amount of TRX user hopes to obtain through withdrawal, the minimum unit.
``` solidity
function withdrawExact(uint256 trxAmount) external returns (uint256)
```

* **Parameter description:**
    * `trxAmount:` the specific amount of TRX.
* **Returns:** the amount of sTRX withdrawn by user, the minimum unit.


<a id="claim-trx"></a>

### **Claim TRX**
Claim the ready-to-be-withdrawn TRX unfrozen in the earliest round.
``` solidity
function claim() external returns (uint256)
```

* **Parameter description:** N/A.
* **Returns:** the amount of TRX claimed by user in the earliest unfreezing round, the minimum unit.

#### **Event**
``` solidity
Claim(address user, uint256 trxAmount)
```

* Emits when user successfully claims TRX.
    * `trxAmount:` the amount of TRX user claims.


<a id="claim-all-unfrozen-trx"></a>

### **Claim all unfrozen TRX**
Claim all ready-to-be-withdrawn, unfrozen TRX
``` solidity
function claimAll() external returns (uint256)
```

* **Parameter description:** N/A.
* **Returns:** the amount of TRX claimed by the user for all expired unfreezing rounds, the minimum unit.


<a id="examples-tronweb"></a>

## **Examples (TronWeb)**

```javascript
const TronWeb = require('tronweb');
const tronWeb = new TronWeb({
  fullHost: 'https://api.trongrid.io',
  headers: { 'TRON-PRO-API-KEY': process.env.TRONGRID_API_KEY },
  privateKey: process.env.PRIVATE_KEY,
});

const STRX = 'TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5'; // sTRX on TRON Mainnet
```

### 1. Stake TRX → receive sTRX

```javascript
async function stake(trxAmount /* in TRX, e.g. 1000 */) {
  const strx = await tronWeb.contract().at(STRX);
  const txId = await strx.deposit().send({
    callValue: trxAmount * 1_000_000, // TRX → sun
    feeLimit: 100_000_000,
  });
  console.log('deposit tx:', txId);
}
```

### 2. Read exchange rate & quote sTRX you'd receive

```javascript
async function quoteStake(trxAmount) {
  const strx = await tronWeb.contract().at(STRX);
  const rate = await strx.exchangeRate().call(); // sTRX per TRX, scaled 1e18
  // strxReceived = trxAmount * 1e18 / rate  (both scaled 1e18 in different ways)
  const trxSun = BigInt(trxAmount) * 1_000_000n;
  const strxReceived = (trxSun * (10n ** 18n)) / BigInt(rate.toString());
  return strxReceived; // in sTRX smallest unit (18 decimals)
}
```

### 3. Unstake sTRX → enters 14-day unbonding queue

```javascript
async function unstake(strxAmountUnits /* in sTRX smallest unit, 18 decimals */) {
  const strx = await tronWeb.contract().at(STRX);
  // Burns sTRX immediately; TRX enters the unfreezing queue.
  const txId = await strx.withdraw(strxAmountUnits).send({ feeLimit: 100_000_000 });
  console.log('withdraw tx:', txId);
}

// Or: specify the exact TRX you want to receive
async function unstakeExact(trxAmountSun) {
  const strx = await tronWeb.contract().at(STRX);
  return strx.withdrawExact(trxAmountSun).send({ feeLimit: 100_000_000 });
}
```

### 4. Claim unfrozen TRX (after the 14-day round completes)

```javascript
async function claim() {
  const strx = await tronWeb.contract().at(STRX);

  // Check whether anything is claimable first
  const claimable = await strx.claimable().call();
  if (claimable.toString() === '0') {
    console.log('nothing to claim yet — unbonding not complete');
    return;
  }

  // claim() returns oldest finished round; claimAll() returns every finished round
  const txId = await strx.claimAll().send({ feeLimit: 100_000_000 });
  console.log('claim tx:', txId);
}
```



