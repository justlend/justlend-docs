# SBM V2

JustLend DAO SBM V2 is a fully upgraded decentralized lending protocol built on the TRON network. It introduces a dual-layer **isolated-collateral lending protocol** composed of Vaults and Markets, along with an Adaptive Curve Interest Rate Model (IRM) for dynamic rate adjustment. The SBM V2 system primarily consists of several core smart contracts — **Moolah Market**, **Moolah Vault**, **TRX Provider**, **Resilient Oracle**, and **Interest Rate Model** — each serving a distinct purpose within the ecosystem:

* **Moolah Market** handles core lending and borrowing operations, including supply, withdrawal, collateral management, and liquidation. **MoolahMarket.sol** allows users to:
    * Supply
    * Withdraw
    * Borrow
    * Repay
    * Supply Collateral
    * Withdraw Collateral
    * Liquidation
* **Moolah Vault** manages pooled user assets, allocates funds to lending markets, and issues transferable shares following the ERC-4626 standard. **MoolahVault.sol** allows users to:
    * Vault Creation
    * Deposit
    * Mint
    * Withdraw
* **TRX Provider** enables seamless interaction between native TRX and wrapped TRX (WTRX), allowing users to supply or borrow using TRX directly. **TRXProvider.sol** allows users to:
    * Deposit
    * Mint
    * Withdraw
    * Redeem
    * Borrow
    * Repay
    * Supply Collateral
    * Withdraw Collateral
* **Resilient Oracle** aggregates multiple price feeds (up to three per token) to ensure reliable and accurate price data for the protocol. 
* **Interest Rate Model (IRM)** dynamically adjusts borrowing and supply rates in real time to maintain market utilization near the optimal level. 

The source code is available on [Github](https://github.com/justlend).

<br>

## **Configuration**

### **1. Position**
In each market, every user has a corresponding Position, which records the user’s supplied, borrowed, and collateralized assets within that market.
``` solidity
struct Position {
  uint256 supplyShares;
  uint128 borrowShares;
  uint128 collateral;
}
```

* `supplyShares:` the number of shares representing the assets a user has supplied to the market.
* `borrowShares:` the number of shares representing the assets a user has borrowed from the market.
* `collateral:` the amount of assets a user has deposited as collateral in the market.


### **2. Market**
``` solidity
struct Market {
  uint128 totalSupplyAssets;
  uint128 totalSupplyShares;
  uint128 totalBorrowAssets;
  uint128 totalBorrowShares;
  uint128 lastUpdate;
  uint128 fee;
}
```

* `totalSupplyAssets:` the total amount of assets supplied to the market and available for lending.
* `totalSupplyShares:` the total number of supply shares in the market.
* `totalBorrowAssets:` the total amount of assets borrowed from the market.
* `totalBorrowShares:` the total number of borrowed shares in the market.
* `lastUpdate:` the timestamp of the last market state update.
* `fee:` the fee rate charged by the market.

**Relationship between assets and shares:** At the beginning, one token corresponds to one share. Over time, as the market generates interest income, the total amount of tokens increases while the total number of shares remains constant. Consequently, each share becomes redeemable for more tokens, allowing users to earn yield when they withdraw their funds.


### **3. MarketParams**
``` solidity
struct MarketParams {
  address loanToken;
  address collateralToken;
  address oracle;
  address irm;
  uint256 lltv;
}
```

* `loanToken:` the address of the token used for borrowing.
* `collateralToken:` the address of the token used as collateral.
* `oracle:` the address of the price oracle contract.
* `irm:` the address of the interest rate model contract.
* `lltv:` the loan-to-value ratio (LTV) that determines the maximum borrowing limit based on the collateral value.


### **4. MarketConfig**
Represents the configuration of each market within the vault.
``` solidity
struct MarketConfig {
  uint176 cap;
  bool enabled;
  MarketType marketType;
  uint64 removableAt;
}
```

* `cap:` the maximum amount of assets that the vault can supply to this market.
* `enabled:` indicates whether the market is active; serves as a switch to control whether investments can be made to the market.
* `marketType:` the type of the market. This is used for compatibility with other lending protocols. Currently, only the Moolah market type is supported.
* `removableAt:` a timestamp indicating when the market can be immediately removed from the withdrawal queue.


### **5. MarketAllocation**
Used when reallocating asset investments across different markets.
``` solidity
struct MarketAllocation {
  MarketParams marketParams;
  uint256 assets;
}
```

* `marketParams:` specifies the target market to which the allocation is applied.
* `assets:` the amount of assets allocated to the specified market.


### **6. Authorization**
The Authorization struct represents the data required to grant or revoke authorization for a specific address.
``` solidity
struct Authorization {
    address authorizer;   
    address authorized;   
    bool isAuthorized;   
    uint256 nonce;        
    uint256 deadline;    
}
```

* `authorizer:` the address that is granting authorization or revocation.
* `authorized:` the address that is being granted or revoked the authorization.
* `isAuthorized:` a boolean indicating whether the authorization is being granted (true) or revoked (false).
* `nonce:` a unique number to prevent replay attacks. This value must be incremented each time a new authorization is signed.
* `deadline:` a timestamp indicating when the authorization will expire. If the current block timestamp exceeds this value, the authorization is no longer valid.


### **7. Signature**
The Signature struct represents the ECDSA (Elliptic Curve Digital Signature Algorithm) signature used to verify that a particular authorization was signed by the authorizer.
``` solidity
struct Signature {
    uint8 v;    
    bytes32 r;    
    bytes32 s;   
}
```

* `v:` the recovery id (0 or 1) used to recover the public key from the signature. It indicates which of the two possible curve points was used for signing.
* `r:` the "r" component of the ECDSA signature, which is derived from the elliptic curve.
* `s:` the "s" component of the ECDSA signature, which is another part of the signature that helps uniquely identify it.

<br>

## **Contracts ABI**

### **Moolah Market**
The JustLend DAO V2 market adopts an isolated-collateral lending protocol, where each market consists of a single collateral asset paired with a single borrowable asset. All markets are managed within the Moolah contract. Each market is uniquely identified by a Market ID, which is composed of the borrowable asset, collateral asset, oracle, interest rate model, and liquidation factor.


#### **1. Supply**
The supply function allows users to provide liquidity to the market for lending.
``` solidity
function supply(MarketParams memory marketParams, uint256 assets, uint256 shares, address onBehalf, bytes calldata data) external returns (uint256 assetsSupplied, uint256 sharesSupplied)
```

* **Parameter description:**
    * `marketParams:` the configuration parameters of the target market (includes loan token, collateral token, oracle, interest rate model, and LTV ratio).
    * `assets:` the amount of tokens the user wants to supply to the market.
    * `shares:` the number of supply shares to mint corresponding to the deposited assets.
    * `onBehalf:` the address that will receive the supply shares. This allows users to supply assets on behalf of another account.
    * `data:` additional encoded data for interaction logic or integrations.

* **Returns:**
    * `assetsSupplied:` the actual amount of tokens supplied.
    * `sharesSupplied:` the actual number of supply shares minted corresponding to the supplied assets.

**Event**
``` solidity
Supply(Id indexed id, address indexed caller, address indexed onBehalf, uint256 assets, uint256 shares)
```

* This event is emitted when assets are supplied to a market.
    * `id:` the unique market identifier (bytes32), representing the market where the supply occurred.
    * `caller:` the address that submitted the transaction.
    * `onBehalf:` the address on whose behalf the assets were supplied, the supply shares are credited to this address.
    * `assets:` the amount of tokens supplied to the market.
    * `shares:` the number of supply shares minted corresponding to the supplied assets.


#### **2. Withdraw**
The withdraw  function allows users to withdraw the previously supplied liquidity from the market.
``` solidity
function withdraw(MarketParams memory marketParams, uint256 assets, uint256 shares, address onBehalf, address receiver) external returns (uint256 assetsWithdrawn, uint256 sharesWithdrawn)
```

* **Parameter description:**
    * `marketParams:` the configuration parameters of the target market (includes loan token, collateral token, oracle, interest rate model, and LTV ratio).
    * `assets:` the amount of tokens to withdraw from the market.
    * `shares:` the number of supply shares to redeem for the corresponding assets.
    * `onBehalf:` the address whose position will be reduced. This enables withdrawals to be made on behalf of another account.
    * `receiver:` the address that will receive the withdrawn assets.

* **Returns:**
    * `assetsWithdrawn:` the actual amount of tokens supplied.
    * `sharesWithdrawn:` the actual number of shares burned corresponding to the withdrawn assets.

**Event**
``` solidity
Withdraw(Id indexed id, address caller, address indexed onBehalf, address indexed receiver, uint256 assets, uint256 shares)
```

* This event is emitted when assets are withdrawn from a market.
    * `id:` the unique market identifier (bytes32), representing the market from which the withdrawal occurred.
    * `caller:` the address that submitted the transaction.
    * `onBehalf:` the address whose supply shares are being withdrawn.
    * `receiver:` the address that receives the withdrawn assets.
    * `assets:` the amount of tokens withdrawn from the market.
    * `shares:` the number of supply shares redeemed corresponding to the withdrawn assets.


#### **3. Borrow**
The borrow function allows users to borrow funds from the SBM V2 market.
``` solidity
function borrow(MarketParams memory marketParams, uint256 assets, uint256 shares, address onBehalf, address receiver) returns (uint256 assetsBorrowed, uint256 sharesBorrowed)
```

* **Parameter description:**
    * `marketParams:` the configuration parameters of the target market (includes loan token, collateral token, oracle, interest rate model, and LTV ratio).
    * `assets:` the amount of tokens the user intends to borrow from the market.
    * `shares:` the number of borrowing shares to mint corresponding to the borrowed assets.
    * `onBehalf:` the address whose position will be increased. This allows borrowing on behalf of another account.
    * `receiver:` the address that will receive the borrowed assets.

* **Returns:**
    * `assetsBorrowed:` the actual amount of tokens borrowed.
    * `sharesBorrowed:` the actual number of shares minted corresponding to the borrowed tokens.

**Event**
``` solidity
Borrow(Id indexed id, address caller, address indexed onBehalf, address indexed receiver, uint256 assets, uint256 shares)
```

* This event is emitted when assets are borrowed from a market.
    * `id:` the unique market identifier (bytes32), representing the market from which the borrowing occurred.
    * `caller:` the address that submitted the transaction.
    * `onBehalf:` the address whose borrowed shares are recorded.
    * `receiver:` the address that receives the borrowed assets.
    * `assets:` the amount of tokens borrowed from the market.
    * `shares:` the number of borrowed shares corresponding to the borrowed assets.
 

#### **4. Repay**
The repay function allows users to repay the funds borrowed from the SBM V2 market.
``` solidity
function repay(MarketParams memory marketParams, uint256 assets, uint256 shares, address onBehalf, bytes calldata data) external returns (uint256 assetsRepaid, uint256 sharesRepaid)
```

* **Parameter description:**
    * `marketParams:` the configuration parameters of the target market (includes loan token, collateral token, oracle, interest rate model, and LTV ratio).
    * `assets:` the amount of tokens to repay to the market.
    * `shares:` the number of borrowing shares to burn corresponding to the repaid assets.
    * `onBehalf:` the address whose borrowing position will be reduced. This enables repayments to be made on behalf of another account.
    * `data:` additional encoded data for interaction logic or integrations.

* **Returns:**
    * `assetsRepaid:` the actual amount of tokens repaid.
    * `sharesRepaid:` the actual number of shares repaid corresponding to the repaid tokens.

**Event**
``` solidity
Repay(Id indexed id, address indexed caller, address indexed onBehalf, uint256 assets, uint256 shares)
```

* This event is emitted when borrowed assets are repaid to the market.
    * `id:` the unique market identifier (bytes32), representing the market where the repayment occurred.
    * `caller:` the address that submitted the transaction.
    * `onBehalf:` the address whose borrowed assets are being repaid.
    * `assets:` the amount of tokens repaid to the market.
    * `shares:` the number of borrowed shares corresponding to the repaid assets.


#### **5. Supply Collateral**
The supply collateral function allows users to supply collateral assets to the SBM V2 market.
``` solidity
function supplyCollateral(MarketParams memory marketParams, uint256 assets, address onBehalf, bytes calldata data)
```

* **Parameter description:**
    * `marketParams:` the configuration parameters of the target market (includes loan token, collateral token, oracle, interest rate model, and LTV ratio).
    * `assets:` the amount of collateral tokens to deposit into the market.
    * `onBehalf:` the address whose collateral position will be increased. This allows users to add collateral on behalf of another account.
    * `data:` additional encoded data for interaction logic or integrations.

* **Returns:** None, reverts on error.

**Event**
``` solidity
SupplyCollateral(Id indexed id, address indexed caller, address indexed onBehalf, uint256 assets)
```

* This event is emitted when collateral is supplied to the market.
    * `id:` the unique market identifier (bytes32), representing the market where the collateral is supplied.
    * `caller:` the address that submitted the transaction.
    * `onBehalf:` the address whose collateral balance is credited.
    * `assets:` the amount of collateral tokens supplied to the market.


#### **6. Withdraw Collateral**
The withdraw collateral function allows users to withdraw their previously supplied collateral from the SBM V2 market.
``` solidity
function withdrawCollateral(MarketParams memory marketParams, uint256 assets, address onBehalf, address receiver)
```

* **Parameter description:**
    * `marketParams:` the configuration parameters of the target market (includes loan token, collateral token, oracle, interest rate model, and LTV ratio).
    * `assets:` the amount of collateral tokens to withdraw from the market.
    * `onBehalf:` the address whose collateral position will be reduced. This allows collateral to be withdrawn on behalf of another account.
    * `receiver:` the address that will receive the withdrawn collateral assets.

* **Returns:** None, reverts on error.

**Event**
``` solidity
WithdrawCollateral(Id indexed id, address caller, address indexed onBehalf, address indexed receiver, uint256 assets)
```

* This event is emitted when collateral is withdrawn from the market.
    * `id:` the unique market identifier (bytes32), representing the market where the collateral is withdrawn.
    * `caller:` the address that submitted the transaction.
    * `onBehalf:` the address whose collateral balance is reduced.
    * `receiver:` the address that receives the withdrawn collateral assets.
    * `assets:` the amount of collateral tokens withdrawn from the market.


#### **7. Liquidate**
The liquidate function allows liquidators to repay a portion of a borrower's debt in exchange for seizing the borrower's collateral when their position becomes undercollateralized.
``` solidity
function liquidate(MarketParams memory marketParams, address borrower, uint256 seizedAssets, uint256 repaidShares, bytes calldata data) external returns(uint256 seizedAssets, uint256 repaidAssets)
```

* **Parameter description:**
    * `marketParams:` the configuration parameters of the target market (includes loan token, collateral token, oracle, interest rate model, and LTV ratio).
    * `borrower:` the address of the user whose position is being liquidated.
    * `seizedAssets:` the amount of collateral assets to be seized from the borrower.
    * `repaidShares:` the number of borrowing shares repaid on behalf of the borrower.
    * `data:` additional encoded data for custom liquidation logic or integrations.

* **Returns:**
    * `seizedAssets:` the actual amount of collateral tokens seized.
    * `repaidAssets:` the actual amount of debt tokens repaid.

**Event**
``` solidity
Liquidate(Id indexed id, address indexed caller, address indexed borrower, uint256 repaidAssets, uint256 repaidShares, uint256 seizedAssets, uint256 badDebtAssets, uint256 badDebtShares)
```

* This event is emitted when a liquidation occurs in the market.
    * `id:` the unique market identifier (bytes32), representing the market where the liquidation takes place.
    * `caller:` the address that submitted the transaction (the liquidator).
    * `borrower:` the address of the borrower being liquidated.
    * `repaidAssets:` the amount of borrowed assets repaid during the liquidation.
    * `repaidShares:` the number of borrowed shares repaid.
    * `seizedAssets:` the amount of collateral assets seized by the liquidator.
    * `badDebtAssets:` the amount of assets classified as bad debt after liquidation.
    * `badDebtShares:` the number of borrowed shares corresponding to the bad debt.


#### **8. Set Authorization**
Sets or updates the authorization status for a specific address.
``` solidity
function setAuthorization(address authorized, bool newIsAuthorized)
```

* **Parameter description:**
    * `authorized:` the address to grant or revoke authorization.
    * `newIsAuthorized:` a boolean indicating the authorization status, true to authorize, false to revoke.

* **Returns:** None, reverts on error.

**Event**
``` solidity
SetAuthorization(address indexed caller, address indexed authorizer, address indexed authorized, bool newIsAuthorized)
```

* This event is emitted when authorization status for an address is updated.
    * `caller:` the address that initiated the transaction.
    * `authorizer:` the address granting the authorization.
    * `authorized:` the address receiving the authorization.
    * `newIsAuthorized:` the new authorization status, true for granted, false for revoked.


#### **9. Set Authorization With Signature**
Sets authorization for an address using an off-chain signature, while recording a nonce to prevent replay attacks.
``` solidity
function setAuthorizationWithSig(Authorization memory authorization, Signature calldata signature)
```

* **Parameter description:**
    * `authorization:` the authorization data structure containing the authorization details.
    * `signature:` the ECDSA signature proving that the authorization was signed by the authorizer.

* **Returns:** None, reverts on error.


#### **10. Accrue Interest**
The accrueInterest function updates the interest accrued in the SBM V2 market based on the latest block timestamp. It synchronizes the market’s supply and borrow states to reflect the most recent interest calculations.
``` solidity
function accrueInterest(MarketParams memory marketParams)
```

* **Parameter description:**
    * `marketParams:` the configuration parameters of the target market (includes loan token, collateral token, oracle, interest rate model, and LTV ratio).

* **Returns:** None, reverts on error.

**Event**
``` solidity
AccrueInterest(Id indexed id, uint256 prevBorrowRate, uint256 interest, uint256 feeShares)
```

* This event is emitted during the execution of functions such as borrow, repay, and supply, which update the market’s borrowing state.
    * `id:` the unique market identifier (bytes32), representing the market where the interest is accrued.
    * `prevBorrowRate:` the previous borrowing rate before the update.
    * `interest:` the number of interest accrued in this update.
    * `feeShares:` the portion of accrued interest distributed to the fee recipient, represented in shares.
 

#### **11. Is Healthy**
Checks whether a borrower’s account in a specific market is healthy. 
``` solidity
function isHealthy(MarketParams memory marketParams, Id id, address borrower) external view returns (bool)
```

* **Parameter description:**
    * `marketParams:` the configuration parameters of the target market (includes loan token, collateral token, oracle, interest rate model, and LTV ratio).
    * `id:` the market’s unique identifier.
    * `borrower:` the address of the borrower whose account health is being checked.

* **Returns:** 
    * **true** means the position is sufficiently collateralized under the current price and LLTV.
    * **false** means the position is undercollateralized and eligible for liquidation, but it does not necessarily mean there is “bad debt” remaining after liquidation.

#### **12. Get Price**
Retrieves the relative price between the collateral token and the loan token in a specific market.
``` solidity
function getPrice(MarketParams memory marketParams) public view returns (uint256)
```

* **Parameter description:**
    * `marketParams:` the configuration parameters of the target market (includes loan token, collateral token, oracle, interest rate model, and LTV ratio).

* **Returns:** the value of one collateral token expressed in loan token units.


#### **13. Get WhiteList**
Retrieves the whitelist of a specified market.
``` solidity
function getWhiteList(Id id) external view returns (address[])
```

* **Parameter description:**
    * `id:` the market’s unique identifier.

* **Returns:** the list of addresses included in the whitelist for the specified market.


#### **14. Is WhiteList**
Checks whether a specific account is included in the whitelist of the market identified by id.
``` solidity
function isWhiteList(Id id, address account) public view returns (bool)
```

* **Parameter description:**
    * `id:` the market’s unique identifier.
    * `account:` the address to check for whitelist eligibility.

* **Returns:** true if the whitelist is not set or if the account is included in it; otherwise, false.


#### **15. Get Liquidation Whitelist**
Retrieves the list of addresses in the liquidation whitelist for the specified market identified by id.
``` solidity
function getLiquidationWhitelist(Id id) external view returns (address[])
```

* **Parameter description:**
    * `id:` the unique identifier of the market.

* **Returns:** a list of addresses authorized to perform liquidation operations in the specified market.


#### **16. Is Liquidation Whitelist**
Checks whether a given account is included in the liquidation whitelist for the specified market.
``` solidity
function isLiquidationWhitelist(Id id, address account) external view returns (bool)
```

* **Parameter description:**
    * `id:` the unique identifier of the market.
    * `account:` the address to be checked in the liquidation whitelist.

* **Returns:** returns true if the account is in the whitelist; otherwise, returns false.


#### **17. Minimum Loan**
Retrieves the minimum loan amount allowed in the specified market.
``` solidity
function minLoan(MarketParams memory marketParams) public view returns (uint256)
```

* **Parameter description:**
    * `marketParams:` the configuration parameters of the target market (includes loan token, collateral token, oracle, interest rate model, and LTV ratio).

* **Returns:** the minimum amount of loan assets that can be borrowed from the market.


#### **18. Get Id**
Returns the unique identifier (ID) corresponding to the specified market.
``` solidity
function getId(MarketParams memory marketParams) external pure returns (bytes32 id)
```

* **Parameter description:**
    * `marketParams:` the configuration parameters of the target market (includes loan token, collateral token, oracle, interest rate model, and LTV ratio).

* **Returns:**
    * `id:` the unique market ID, calculated as keccak256(marketParams).
 

#### **19. Paused**
Checks whether the market is globally paused.
``` solidity
function paused() public view virtual returns (bool)
```

* **Parameter description:** N/A.

* **Returns:** true if the protocol is globally paused and all markets are disabled; false otherwise.


#### **20. Borrow Rate Full View**
Retrieves both the average borrow rate of a given market since the last update and the current borrow rate at the target utilization level.
``` solidity
function borrowRateFullView(Id id) public view returns (uint256 avgBorrowRate, int256 targetBorrowRate)
```

* **Parameter description:**
    * `id:` the unique market ID.

* **Returns:**
    * `avgBorrowRate:` the average borrow rate since the last interest update.
    * `targetBorrowRate:` the current borrow rate at the target utilization level.

<br> 

### **Moolah Valut**
A Vault is a single-asset management contract that provides borrowable assets to the market and can be created by anyone. Each vault operates as an independent contract managed by a designated fund manager, who can configure which markets to supply liquidity to. When users deposit assets into the vault, the funds are automatically allocated to the configured markets. The fund manager also has the ability to reallocate funds across markets. The vault follows the ERC-4626 standard (an extension of ERC-20 for tokenized vaults), allowing users to mint transferable shares upon depositing assets.

#### **1. Create Moolah Vault**
Creates a new MoolahVault and returns the addresses of the created vault and related contracts. The MoolahVault itself acts as a token. Users receive transferable vault shares when depositing assets.
``` solidity
function createMoolahVault(address manager, address curator, address guardian, uint256 timeLockDelay, address asset, string memory name, string memory symbol) external returns (address vault, address managerTimeLock, address curatorTimeLock)
```

* **Parameter description:**
    * `manager:` the address with manager privileges in the MoolahVault’s TimeLock contract.
    * `curator:` the address with curator privileges in the TimeLock contract.
    * `guardian:` the address responsible for emergency control or protection actions.
    * `timeLockDelay:` the delay period for executing TimeLock transactions.
    * `asset:` the address of the asset managed by MoolahVault.
    * `name:` the name of the MoolahVault token.
    * `symbol:` the symbol of the MoolahVault token.

* **Returns:**
    * `vault:` the address of the newly created MoolahVault contract.
    * `managerTimeLock:` the address of the Manager Timelock contract for the vault.
    * `curatorTimeLock:` the address of the Curator Timelock contract for the vault.
      
**Event**
``` solidity
CreateMoolahVault(address indexed moolahVault, address implementation, address managerTimeLock, address curatorTimeLock, uint256 timeLockDelay, address indexed caller, address manager, address curator, address guardian, address indexed asset, string name, string symbol)
```

* This event is emitted when a new MoolahVault is created.
    * `moolahVault:` the address of the newly created MoolahVault.
    * `implementation:` the implementation contract address used by the vault.
    * `managerTimeLock:` the TimeLock contract address for the manager.
    * `curatorTimeLock:` the TimeLock contract address for the curator.
    * `timeLockDelay:` the delay period (in seconds) for executing TimeLock transactions.
    * `caller:` the address that initiated the creation transaction.
    * `manager:` the address assigned as the manager in the TimeLock contract.
    * `curator:` the address assigned as the curator in the TimeLock contract.
    * `guardian:` the guardian address responsible for vault protection or emergency actions.
    * `asset:` the address of the underlying asset managed by the vault.
    * `name:` the name of the MoolahVault token.
    * `symbol:` the symbol of the MoolahVault token.


#### **2. Set Vault Admin**
Sets the address of the Vault Administrator.
``` solidity
function setVaultAdmin(address _vaultAdmin)
```

* **Parameter description:**
    * `_vaultAdmin:` the address to be assigned as the Vault Administrator.

* **Returns:** None, reverts on error.

**Event**
``` solidity
SetVaultAdmin(address vaultAdmin)
```

* This event is emitted when the Vault Administrator address is set.
    * `vaultAdmin:` the address assigned as the new Vault Administrator.
 

#### **3. Deposit**
Deposits assets into the vault.
``` solidity
function deposit(uint256 assets, address receiver) public returns (uint256 shares)
```

* **Parameter description:**
    * `assets:` the amount of assets to deposit into the vault.
    * `receiver:` the address that will receive the minted vault shares.

* **Returns:**
    * `shares:` the number of vault shares minted to the receiver in exchange for the deposited assets.

**Event**
``` solidity
Deposit(address indexed sender, address indexed owner, uint256 assets, uint256 shares)
```

* This event is emitted when a user deposits assets into the vault.
    * `sender:` the address that initiated the deposit transaction.
    * `owner:` the address that owns the deposited assets.
    * `assets:` the amount of assets deposited by the user.
    * `shares:` the number of vault shares minted to the user corresponding to the deposited assets.


#### **4. Mint**
Mints vault shares by depositing the corresponding amount of assets.
``` solidity
function mint(uint256 shares, address receiver) public override returns (uint256 assets)
```

* **Parameter description:**
    * `shares:` the number of vault shares to mint.
    * `receiver:` the address that will receive the minted shares.

* **Returns:**
    * `assets:` the amount of assets required to mint the specified number of shares.


#### **5. Withdraw**
Withdraws assets from the vault by burning the corresponding number of shares.
``` solidity
function withdraw(uint256 assets, address receiver, address owner) public override returns (uint256 shares)
```

* **Parameter description:**
    * `assets:` the amount of assets to withdraw from the vault.
    * `receiver:` the address that will receive the withdrawn assets.
    * `owner:` the address that owns the withdrawn assets.

* **Returns:**
    * `shares:` the  number of shares burned corresponding to the withdrawn assets.

**Event**
``` solidity
Withdraw(address indexed sender, address indexed receiver, address indexed owner, uint256 assets, uint256 shares)
```

* This event is emitted when a user withdraws assets from the vault.
    * `sender:` the address that initiated the withdrawal transaction.
    * `receiver:` the address that receives the withdrawn assets.
    * `owner:` the address that owns the withdrawn assets.
    * `assets:` the amount of assets withdrawn from the vault.
    * `shares:` the number of vault shares burned to redeem the withdrawn assets.


#### **6. Is WhiteList**
Checks whether a specific account is included in the whitelist.
``` solidity
function isWhiteList(address account) public view returns (bool)
```

* **Parameter description:**
    * `account:` the address to check.

* **Returns:** returns true if the account is on the whitelist; otherwise, returns false.


#### **7. Get WhiteList**
Retrieves the list of addresses currently included in the whitelist.
``` solidity
function getWhiteList() external view returns (address[])
```

* **Parameter description:** N/A.

* **Returns:** an array containing all addresses that are on the whitelist.


#### **8. Supply Queue Length**
Returns the total number of markets currently in the supply queue.
``` solidity
function supplyQueueLength() external view returns (uint256)
```

* **Parameter description:** N/A.

* **Returns:** the length of the supply queue.


#### **9. Withdraw Queue Length**
Returns the total number of markets currently in the withdrawal queue.
``` solidity
function withdrawQueueLength() external view returns (uint256)
```

* **Parameter description:** N/A.

* **Returns:** the length of the withdrawal queue.


#### **10. Maximum Deposit**
Returns the maximum amount of assets that can be deposited into the vault.
``` solidity
function maxDeposit(address) public view override returns (uint256)
```

* **Parameter description:**
    * `address:` the address of the depositor. 

* **Returns:** the maximum amount of assets that can be deposited.


#### **11. Maximum Mint**
Returns the maximum number of shares that can be minted, corresponding to maxDeposit, with the asset amount converted into shares.
``` solidity
function maxMint(address) public view override returns (uint256)
```

* **Parameter description:**
    * `address:` the address of the minter.

* **Returns:** the maximum number of shares that can be minted.


#### **12. Maximum Withdraw**
Returns the maximum amount of assets that a user can withdraw from the vault.
``` solidity
function maxWithdraw(address owner) public view override returns (uint256 assets)
```

* **Parameter description:**
    * `owner:` the address of the user whose withdrawable balance is being queried.

* **Returns:** 
    * `assets:` the maximum amount of assets that can be withdrawn by the specified user.


#### **13. Maximum Redeem**
Returns the maximum number of shares that a user can redeem from the vault.
``` solidity
function maxRedeem(address owner) public view override returns (uint256)
```

* **Parameter description:**
    * `owner:`  the address of the user whose redeemable shares are being queried.

* **Returns:** the maximum number of shares that can be redeemed by the specified user.


<br> 

### **TRX Provider**
Since both the Moolah Market and Moolah Vault operate with TRC20 tokens, WTRX is used as a wrapped version of TRX. Users can interact directly with TRX through the TRX Provider, which internally handles the conversion between TRX and WTRX before executing the corresponding operations in the market or vault.


#### **1. Deposit**
When users stake TRX, the TRX Provider automatically converts TRX into WTRX and deposits it into the corresponding Vault.
``` solidity
// Deposit without specifying a vault
function deposit(address receiver) external payable returns (uint256 shares)

// Deposit with a specified vault
function deposit(address vault, address receiver) public payable returns (uint256 shares)
```

* **Parameter description:**
    * `valut:` the address of the specific Vault where the converted WTRX will be deposited. If not specified, the system automatically deposits into the default Vault configured by the TRX Provider.
    * `receiver:` the address that will receive the minted vault shares corresponding to the deposited assets.

* **Returns:**
    * `shares:` the number of vault shares minted for the receiver based on the amount of TRX (converted to WTRX) deposited into the specified vault.


#### **2. Mint**
This function stakes TRX similar to the deposit function, but instead of specifying the asset amount, users specify the number of shares they wish to mint. The TRX Provider converts the provided TRX into WTRX and deposits it into the vault.
``` solidity
// Mint without specifying a vault
function mint(uint256 shares, address receiver) external payable returns (uint256 assets)

// Mint with a specified vault
function mint(address vault, uint256 shares, address receiver) public payable returns (uint256 assets)
```

* **Parameter description:**
    * `valut:` the address of the specific Vault where the converted WTRX will be deposited. If not specified, the system automatically deposits into the default Vault configured by the TRX Provider.
    * `shares:` the number of vault shares to mint.
    * `receiver:` the address that will receive the minted vault shares corresponding to the deposited assets.

* **Returns:**
    * `assets:` the amount of TRX (converted to WTRX) required to mint the specified number of shares.


#### **3. Withdraw**
Withdraws TRX. The TRX Provider retrieves the corresponding amount of WTRX from the vault, converts it back to TRX, and transfers it to the user.
``` solidity
// Withdraw without specifying a vault
function withdraw(uint256 assets, address payable receiver, address owner) external returns (uint256 shares)

// Withdraw with a specified vault
function withdraw(address vault, uint256 assets, address payable receiver, address owner) external returns (uint256 shares)
```

* **Parameter description:**
    * `valut:` the address of the specific Vault where the converted WTRX will be deposited. If not specified, the system automatically deposits into the default Vault configured by the TRX Provider.
    * `assets:` the amount of TRX to withdraw (converted from WTRX).
    * `receiver:` the address that will receive the withdrawn TRX.
    * `owner:` the address that owns the withdrawn assets (payer of the shares).

* **Returns:**
    * `shares:` the number of shares burned in exchange for the specified amount of TRX.


#### **4. Redeem**
Withdraws TRX. Similar to withdrawal, but instead of specifying the withdrawal amount, the user specifies the number of shares to redeem. The TRX Provider retrieves the corresponding amount of WTRX from the vault, converts it back to TRX, and transfers it to the user.
``` solidity
// Redeem without specifying a vault
function redeem(uint256 shares, address payable receiver, address owner) external returns (uint256 assets)

// Redeem with a specified vault
function redeem(address vault, uint256 shares, address payable receiver, address owner) external returns (uint256 assets)
```

* **Parameter description:**
    * `valut:` the address of the vault from which WTRX will be redeemed. If not specified, the default vault is used.
    * `shares:` the number of shares to redeem.
    * `receiver:` the address that will receive the redeemed TRX.
    * `owner:` the address that owns the redeemed shares.

* **Returns:**
    * `assets:` the amount of TRX received from redeeming the specified shares.


#### **5. Borrow**
Borrows TRX from the specified market. The TRX Provider interacts with the underlying vault and market contracts to withdraw the corresponding WTRX, converts it to TRX, and sends it to the user.
``` solidity
function borrow(MarketParams calldata marketParams, uint256 assets, uint256 shares, address onBehalf, address payable receiver) external returns (uint256 _assets, uint256 _shares)
```

* **Parameter description:**
    * `marketParams:` the parameters identifying the market (including borrowable asset, collateral asset, oracle, interest rate model, and liquidation factor).
    * `assets:` the amount of TRX to borrow.
    * `shares:` the corresponding share amount representing the borrowed position.
    * `onBehalf:` the address on whose behalf the borrowing is executed.
    * `receiver:` the address that will receive the borrowed TRX.

* **Returns:**
    * `_assets:` the actual amount of TRX borrowed.
    * `_shares:` the number of shares corresponding to the borrowed assets.


#### **6. Repay**
Repays borrowed TRX. When a user repays, the TRX Provider converts the sent TRX into WTRX internally and uses it to repay the corresponding market debt.
``` solidity
function repay(MarketParams calldata marketParams, uint256 assets, uint256 shares, address onBehalf, bytes calldata data) external payable returns (uint256 _assets, uint256 _shares)
```

* **Parameter description:**
    * `marketParams:` the parameters identifying the market (including borrowable asset, collateral asset, oracle, interest rate model, and liquidation factor).
    * `assets:` the amount of TRX to repay.
    * `shares:` the share amount corresponding to the repaid assets.
    * `onBehalf:` the address on whose behalf the repayment is made.
    * `data:` additional data that can be used for callback or custom logic.

* **Returns:**
    * `_assets:` the actual amount of TRX repaid.
    * `_shares:` the number of shares corresponding to the repaid amount.


#### **7. Supply Collateral**
Supplies TRX as collateral. When a user provides collateral in TRX, the TRX Provider automatically wraps TRX into WTRX and deposits it into the corresponding market as collateral.
``` solidity
function supplyCollateral(MarketParams calldata marketParams, address onBehalf, bytes calldata data) external payable
```

* **Parameter description:**
    * `marketParams:` the parameters identifying the market (including borrowable asset, collateral asset, oracle, interest rate model, and liquidation factor).
    * `onBehalf:` the address on whose behalf the collateral is supplied.
    * `data:` additional data that can be used for callback or custom logic.

* **Returns:** None, reverts on error.


#### **8. Withdraw Collateral**
Withdraws TRX collateral. When a user withdraws collateral, the TRX Provider retrieves WTRX from the market, unwraps it into TRX, and transfers it to the specified receiver.
``` solidity
function withdrawCollateral(MarketParams calldata marketParams, uint256 assets, address onBehalf, address payable receiver)
```

* **Parameter description:**
    * `marketParams:` the parameters identifying the market (including borrowable asset, collateral asset, oracle, interest rate model, and liquidation factor).
    * `assets:` the amount of collateral (in TRX) to withdraw.
    * `onBehalf:` the address from which the collateral is withdrawn.
    * `receiver:` the address that receives the withdrawn TRX.

* **Returns:** None, reverts on error.


<br> 

### **Resilient Oracle**
The Resilient Oracle is an aggregated price feed contract that supports configuring up to three price sources (in Chainlink API format) for each token. It allows querying the price of any token, with a precision of 18 decimals.


#### **1. Peek**
Retrieves the price of a specified token.
``` solidity
function peek(address asset) external view override returns (uint256)
```

* **Parameter description:**
    * `asset:` the token address to query.

* **Returns:** the current price of the token (with 18-decimal precision).


<br> 

### **Interest Rate Model**
JustLend DAO SBM V2 adopts the Adaptive Curve Interest Rate Model, an enhanced version of the Jump Curve model from JustLend DAO SBM V1. This upgraded model introduces dynamic adjustments, enabling interest rates to automatically adapt in real time to maintain market utilization around the optimal target level.


#### **1. Default TargetUtilization**
This value defines the optimal utilization level that the interest rate model aims to maintain. Under normal circumstances, it remains constant and only changes when the underlying interest rate model implementation is replaced.
``` solidity
function defaultTargetUtilization() external view returns (int256)
```

* **Parameter description:** N/A.

* **Returns:** the default target utilization rate of the market.


#### **2. Target Utilization**
If the market has a non-zero target utilization rate configured, that value is returned. Otherwise, the function returns the default target utilization rate.
``` solidity
function targetUtilization(Id id) public view returns (int256)
```

* **Parameter description:**
    * `id:` the unique identifier of the market.   

* **Returns:** the target utilization rate for a specific market.
