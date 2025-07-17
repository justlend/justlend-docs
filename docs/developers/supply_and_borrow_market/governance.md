# Governance

JustLend DAO protocol is governed and upgraded by JST holders. There are three components included in the governance system: [JST](https://tronscan.org/#/token20/TCFLL5dx5ZJdKnWuesXxi1VPwjLVmWZZy9)([WJST](https://tronscan.org/#/contract/TXk9LnTnLN7oH96H3sKxJayMxLxR9M4ZD6/code)) token,
governance module([GovernorBravo](https://tronscan.org/#/contract/TEqiF5JbhDPD77yjEfnEMncGRZNDt2uogD/code)) and [Timelock](https://tronscan.org/#/contract/TRWNvb15NmfNKNLhQpxefFz7cNjrYjEw7x). The governance of the JustLend DAO protocol is through proposals, whose process can be summarized as proposal posting-voting-taking effect.

`GovernorBravoDelegate.sol:` allows users to:

* Propose
* Queue
* Execute
* Cancel
* Deposit
* Vote

The source code is available on [Github](https://github.com/justlend/justlend-protocol/blob/main/contracts/Governance/Bravo/GovernorBravoDelegate.sol).


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
Calling this method gets the votes of a specified voter on a proposal.
``` solidity
function getReceipt(uint proposalId, address voter) public view returns (Receipt memory)

struct Receipt {
    bool hasVoted;
    bool support;
    uint256 votes;
}}
```

* **Parameter description:**
    * `proposalId:` ID of the proposal.
    * `voter:` address of the specified account.
* **Returns:**
    * `hasVoted:` voted or not;
    * `values:` for or against;
    * `signatures:` vote count.


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
Calling this method exchanges JST for WJST at a one-to-one ratio.
``` solidity
function deposit(uint256 sad) public
```

* **Parameter description:**
    * `sad:` number of votes(WJST) to exchange.
* **Returns:** None, reverts on error.


### **Cast Vote**
Calling this method casts a vote on a proposal. The voting weight will be calculated at the time the proposal's state becomes active.
``` solidity
function castVote(uint proposalId, uint votes, bool support) public
```

* **Parameter description:**
    * `proposalId:` ID of the proposal to vote;
    * `votes:` number of the votes to be cast;
    * `support:` for or against.
* **Returns:** None, reverts on error.


### **Cast Vote With Reason**
Calling this method casts a vote on a proposal. The reason can be submitted simultaneously.
``` solidity
function castVoteWithReason(uint proposalId, uint votes, bool support, string calldata reson) public
```

* **Parameter description:**
    * `proposalId:` ID of the proposal to vote;
    * `vote:` number of the votes to be cast;
    * `support:` for or against;
    * `reason:` voting reason.
* **Returns:** None, reverts on error.


### **Cast Vote By Signature**
Calling this method casts votes on a specified proposal. Comparing with `castVote()`, this method allows offline signature.
``` solidity
function castVoteWithReason(uint proposalId, uint votes, bool support, string calldata reson) public
```

* **Parameter description:**
    * `proposalId:` ID of the proposal to vote;
    * `vote:` number of the votes to be cast;
    * `support:` for or against;
    * `v:` recover byte of the signature;
    * `r:` half of the ECDSA signature pair;
    * `s:` half of the ECDSA signature pair.
* **Returns:** None, reverts on error.
