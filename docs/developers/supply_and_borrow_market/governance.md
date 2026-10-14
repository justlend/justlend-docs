---
title: Governance — GovernorBravo + WJST + Timelock
description: JustLend DAO governance contract reference — propose, vote, queue, execute through GovernorBravo. JST → WJST 1:1 wrapping gives voting power; a 48-hour Timelock executes successful proposals.
---

# Governance

!!! info "About this page"
    * **Protocol:** JustLend DAO
    * **Network:** TRON Mainnet
    * **Components:** `JST` (TRC20, `TCFLL5dx5ZJdKnWuesXxi1VPwjLVmWZZy9`) → `WJST` (voting wrapper, deposit JST → receive WJST 1:1) → `GovernorBravoDelegator` (entrypoint, `TEqiF5JbhDPD77yjEfnEMncGRZNDt2uogD`) → `GovernorBravoDelegate` (impl, `TUeNh9BsYK44XePmFAuKZWg2rJuU7bSt5u`) → `Timelock` (executor, `TRWNvb15NmfNKNLhQpxefFz7cNjrYjEw7x`, **`delay() = 172,800 sec = 48 hours`** verified on-chain). **Always call the Delegator**, not the Delegate.
    * **Voting power:** 1 JST wrapped as WJST = 1 whole vote. Approval requires For votes > Against votes AND For votes >= 600,000,000 (`quorumVotes()`). Non-whitelisted proposers need available WJST strictly greater than 200,000,000 (`proposalThreshold()`), not merely that many JST in a wallet.
    * **Lifecycle states:** `Pending → Active → (Canceled | Defeated | Succeeded) → Queued → Executed | Expired`. 
    * **On-chain timing (read on 2026-10-14):** `votingDelay() = 1 block`, `votingPeriod() = 86,400 blocks ≈ 3 days`, Timelock `delay() = 48 hours`. For creation at block B, B+1 is still Pending; the earliest Active block is B+2. Read `state(proposalId)` before voting. The **off-chain ~2-day forum discussion** is a community norm, not a contract-enforced review period; it does not remove the on-chain block boundary.
    * **ABI:** [`abis/governor-alpha.json`](../abis/governor-alpha.json) (Governor) + [`abis/wjst.json`](../abis/wjst.json) (voting wrapper) 
    * **Implementation check:** `implementation()` on the Governor proxy returned the implementation above on **2026-10-14**, agreeing with the 2026-10-12 read. This corrects a documentation pointer; it does not deploy or upgrade a contract, and the entrypoint remains the proxy. See [address verification](../deployed_contracts.md#address-verification) and [ABI provenance](../abis/index.md#scope-and-provenance). Re-read it after an upgrade.
    * **Discussion forum** (off-chain, pre-proposal): <https://forum.justlend.org>.

JustLend DAO protocol is governed and upgraded by JST holders. There are three components included in the governance system: [JST](https://tronscan.org/#/token20/TCFLL5dx5ZJdKnWuesXxi1VPwjLVmWZZy9)([WJST](https://tronscan.org/#/contract/TXk9LnTnLN7oH96H3sKxJayMxLxR9M4ZD6/code)) token,
governance module([GovernorBravo](https://tronscan.org/#/contract/TEqiF5JbhDPD77yjEfnEMncGRZNDt2uogD/code)) and [Timelock](https://tronscan.org/#/contract/TRWNvb15NmfNKNLhQpxefFz7cNjrYjEw7x). The governance of the JustLend DAO protocol is through proposals, whose process can be summarized as proposal posting-voting-taking effect.

`GovernorBravoDelegate.sol:` allows users to:

* Propose
* Queue
* Execute
* Cancel
* Vote

JST deposit, vote unlocking, and JST withdrawal are calls to **WJST**, not GovernorBravo.

The source code is available on [Github](https://github.com/justlend/justlend-protocol/blob/main/contracts/Governance/Bravo/GovernorBravoDelegate.sol).


## Governance boundaries and evidence

The Mainnet proxy getters were read on **2026-10-14**: `proposalThreshold() = 2e26`, `quorumVotes() = 6e26`, `votingDelay() = 1`, and `votingPeriod() = 86400`. WJST voting amounts use 18-decimal raw units. Getters establish parameter values, not comparison operators; the operators below come from the [pinned GovernorBravo `propose` implementation](https://github.com/justlend/justlend-protocol/blob/f28f3b462a4f281761e23423554563e15fc9f028/contracts/Governance/Bravo/GovernorBravoDelegate.sol#L74-L91) and [`state` implementation](https://github.com/justlend/justlend-protocol/blob/f28f3b462a4f281761e23423554563e15fc9f028/contracts/Governance/Bravo/GovernorBravoDelegate.sol#L207-L226). These are source-level rules, not a claim that live boundary transactions were submitted.

- **Proposal balance gate:** `availableVotes > proposalThreshold || isWhitelisted`. Exactly 200,000,000 WJST does **not** pass for a non-whitelisted proposer; one additional raw unit does pass this balance gate. A current whitelist entry bypasses only this gate, not the other `propose()` checks. The [pinned WJST `getPriorVotes` implementation](https://github.com/justlend/justlend-protocol/blob/f28f3b462a4f281761e23423554563e15fc9f028/contracts/Governance/WJST.sol#L93-L96) returns the available balance, despite its historical-sounding name; JST not deposited into WJST and votes already locked are not available voting balance.
- **Approval vote gate:** `forVotes > againstVotes && forVotes >= quorumVotes`. Exactly 600,000,000 For-votes meets quorum; a tie with Against still fails. This gate is evaluated after voting ends, for a proposal that has not been canceled.
- **Pending block condition:** `blockNumber <= startBlock`, where `startBlock = creationBlock + votingDelay`.
- **Active block condition:** `startBlock < blockNumber && blockNumber <= endBlock`, where `endBlock = startBlock + votingPeriod`. For a non-canceled proposal created at B with delay 1, B and B+1 are Pending; B+2 is the earliest Active block, and endBlock is still Active. Block timing is not a wall-clock guarantee.

Re-read the parameters and implementation after upgrades. Approval is not execution: a successful proposal must be queued, then wait the Timelock delay before `execute()` can be called.

## **Proposals**

### **Propose**
Calling this method creates a proposal to change & update the JustLend DAO protocol.
``` solidity
function propose(address[] memory targets, uint[] memory values, string[] memory signatures, bytes[] memory calldatas, string memory description) public returns (uint)
```

* **Parameter description:**
    * `targets:` target addresses for calls to be made during proposal execution;
    * `values:` values to be passed to the calls;
    * `signatures:` function signatures;
    * `calldatas:` data for each function;
    * `description:` a readable message of what exactly the proposal changes.
* **Returns:** the ID of this proposal.


### **Queue**
Calling this method moves a successful proposal into the Timelock waiting period. The waiting period begins when this method is successfully called.
``` solidity
function queue(uint proposalId) public
```

* **Parameter description:**
    * `proposalId:` ID of the successful proposal.
* **Returns:** None, reverts on error.


### **Execute**
Calling this method executes the proposal whose waiting period has already been ended. Actions in the proposal will be invoked during the execution.
``` solidity
function execute(uint proposalId) public payable
```

* **Parameter description:**
    * `proposalId:` ID of the proposal to be executed.
* **Returns:** None, reverts on error.


### **Cancel**
Calling this function cancels a proposal. A proposal can be cancelled at any time prior to its execution.
``` solidity
function cancel(uint proposalId) public
```

* **Parameter description:**
    * `proposalId:` ID of the proposal to be cancelled.
* **Returns:** None, reverts on error.


### **Get Actions**
Calling this method gets the actions of an exact proposal.
``` solidity
function getActions(uint proposalId) public view returns (address[] memory targets, uint[] memory values, string[] memory signatures, bytes[] memory calldatas)
```

* **Parameter description:**
    * `proposalId:` ID of the proposal.
* **Returns:**
    * `targets:` target addresses for calls to be made during proposal execution;
    * `values:` values to be passed to the calls;
    * `signatures:` function signatures;
    * `calldatas:` data for each function.


### **Get Receipt**
Calling this method gets the receipt of a specified voter on a proposal.
``` solidity
function getReceipt(uint proposalId, address voter) public view returns (Receipt memory)

struct Receipt {
    bool hasVoted;
    uint8 support;
    uint96 votes;
}
```

* **Parameter description:**
    * `proposalId:` ID of the proposal.
    * `voter:` address of the specified account.
* **Returns:**
    * `hasVoted:` voted or not;
    * `support:` `0` = against, `1` = for, `2` = abstain; interpret it only when `hasVoted` is true;
    * `votes:` total recorded vote weight for this voter on this proposal, in 18-decimal WJST raw units.

The result is **one tuple** with these three components, not three unrelated proposal-action fields. The downloadable ABI expands the tuple using the official [`Receipt` source definition](https://github.com/justlend/justlend-protocol/blob/f28f3b462a4f281761e23423554563e15fc9f028/contracts/Governance/Bravo/GovernorBravoInterfaces.sol); the node's `getcontract` response only labels the output `tuple` and omits its components. See [ABI scope and provenance](../abis/index.md#scope-and-provenance) before assuming full deployment-artifact coverage.


### **Proposal State**
Calling this method returns the state of a specified proposal.
``` solidity
function state(uint proposalId) public view returns (ProposalState)
```

* **Parameter description:**
    * `proposalId:` ID of the specified proposal;
* **Returns:**
    * `ProposalState:` Pending or Active or Canceled; Defeated or Succeeded or Queued; Expired or Executed.



## **Poll & Vote**

### **Deposit**
Call this method on **WJST** (`TXk9LnTnLN7oH96H3sKxJayMxLxR9M4ZD6`) to exchange JST for WJST at a one-to-one ratio. First approve WJST to spend the requested JST amount. Do not call `deposit` on the Governor proxy.
``` solidity
function deposit(uint256 amount) public
```

* **Parameter description:**
    * `amount:` JST raw units to wrap (18 decimals; `10^18` raw units = 1 JST = 1 whole vote).
* **Returns:** None, reverts on error.


### **Cast Vote**
Calling this method casts a vote on a proposal. Voting weight is determined based on the voter’s available WJST balance when the vote is cast, and the corresponding WJST is locked for the proposal.
``` solidity
function castVote(uint256 proposalId, uint256 votes, uint8 support) external
```

* **Parameter description:**
    * `proposalId:` ID of the proposal to vote;
    * `votes:` desired **total** recorded vote weight on this proposal in 18-decimal WJST raw units, not an incremental amount. On a repeat vote, the same support choice must be retained; only the increase above the previous receipt is newly locked, subject to available WJST;
    * `support:` `0` = against, `1` = for, `2` = abstain.
* **Returns:** None, reverts on error.


### **Cast Vote With Reason**
Calling this method casts a vote on a proposal. The reason can be submitted simultaneously.
``` solidity
function castVoteWithReason(uint256 proposalId, uint256 votes, uint8 support, string calldata reason) external
```

* **Parameter description:**
    * `proposalId:` ID of the proposal to vote;
    * `votes:` desired total recorded weight, in 18-decimal WJST raw units, as for `castVote`;
    * `support:` `0` = against, `1` = for, `2` = abstain;
    * `reason:` voting reason.
* **Returns:** None, reverts on error.


### **Cast Vote By Signature**
Calling this method casts votes on a specified proposal. Comparing with `castVote()`, this method allows offline signature.
``` solidity
function castVoteBySig(uint256 proposalId, uint256 votes, uint8 support, uint8 v, bytes32 r, bytes32 s) external
```

* **Parameter description:**
    * `proposalId:` ID of the proposal to vote;
    * `votes:` desired total recorded weight, in 18-decimal WJST raw units;
    * `support:` `0` = against, `1` = for, `2` = abstain;
    * `v:` recover byte of the signature;
    * `r:` half of the ECDSA signature pair;
    * `s:` half of the ECDSA signature pair.
* **Returns:** None, reverts on error.

These input types were checked against the ABI of Mainnet's current implementation, `TUeNh9BsYK44XePmFAuKZWg2rJuU7bSt5u`, on **2026-10-12**. Submit to the **Governor proxy**; offline signing is not a read-only vote, and execution still requires a transaction. Construct the signature domain for the correct network and proxy, not the implementation address.

### **Available votes, locks, and withdrawal**

The deployed WJST's published [`getPriorVotes(account, blockNumber)` implementation](https://github.com/justlend/justlend-protocol/blob/f28f3b462a4f281761e23423554563e15fc9f028/contracts/Governance/WJST.sol) ignores `blockNumber` and returns the account's **current available WJST balance**. It is not a historical proposal-block snapshot. Voting invokes `voteFresh` through the Governor, moving the incremental voted amount out of the available balance into the proposal-specific lock.

After the proposal is no longer Pending or Active (`state(proposalId) >= 2`), the voter may call **`WJST.withdrawVotes(proposalId)`** to restore those locked votes to their available WJST balance. This unlock step does not itself return JST. **`WJST.withdraw(amount)`** then burns available WJST and returns JST 1:1; it cannot spend still-locked votes. Both operations are state-changing and require wallet confirmation. A proposal ending does not automatically withdraw tokens.
