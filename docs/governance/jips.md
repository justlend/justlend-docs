---
title: JustLend Improvement Proposals (JIPs)
description: How the JustLend proposal lifecycle works — discussion on the forum, on-chain submission via GovernorBravo, 3-day voting period, 48-hour Timelock, then execution. Non-whitelisted proposers need more than 200M available WJST.
---

# JustLend Improvement Proposals

!!! info "About this page"
    **Protocol:** JustLend
    **Network:** TRON Mainnet
    **Scope:** the user-facing proposal lifecycle.
    **Lifecycle (on-chain):** `propose()` on `GovernorBravoDelegator` (`TEqiF5JbhDPD77yjEfnEMncGRZNDt2uogD`) → Pending → Active → voting for `86,400 blocks ≈ 3 days` → `queue()` → 48-hour Timelock → `execute()`. With `votingDelay() = 1`, a proposal created at B remains Pending at B+1 and can first be Active at B+2.
    **Off-chain norm:** community discussion for ~2 days on <https://forum.justlend.org> before proposing is not protocol-enforced; the on-chain block boundary still applies.
    **Approval threshold:** For votes > Against votes AND For votes >= 600,000,000. 
    **Proposal threshold:** available WJST strictly greater than 200,000,000 for a non-whitelisted proposer. Parameters were read on 2026-10-14; see [governance boundaries and evidence](../developers/supply_and_borrow_market/governance.md#governance-boundaries-and-evidence).

The JUST DAO introduces a structured approach to decentralizing the JustLend protocol and empowering community autonomy. JUST DAO fosters consensus among all participants in the JustLend ecosystem through governance mechanisms and economic incentives. The protocol's functions and the JST token serve as core security elements of the JustLend protocol.

Governance mechanisms in decentralized protocols are driven by participation, incentives, self-regulation, and policy management within the community, adapting to and coexisting with the market dynamics. JUST DAO manages on-chain operations through proposals, enabling the protocol to achieve self-operation, self-governance, and self-evolution based on predefined rules through intelligent management and token economic incentives, without third-party intervention, ultimately maximizing efficiency and value transfer.

An essential incentive method in the governance process of JUST DAO, JST tokenizes various organizational elements, integrating monetary capital, human capital, and other resources to enhance organizational efficiency significantly. The goal of the JST economy is to facilitate the virtuous and long-term development of the entire Justlend ecosystem, allowing stakeholders and investors to benefit from a more secure agreement. JST holders are accountable for the protocol and ecosystem, contributing through practical actions such as technical integration (e.g., DeFi front-end integration) or financial investments (e.g., liquidity provision), significantly enhancing protocol execution, security, and functionality.

The JUST DAO was established to facilitate the development and long-term governance of the JustLend protocol. The goal is to create a future-proof governance framework leveraging system incentives and multi-level governance to maintain an effective balance that drives long-term growth and continuous protocol optimization.

### **Governance Process**

JustLend governance uses JST deposited into WJST to acquire voting power for JustLend Improvement Proposals (JIPs). Proposals are typically discussed in the [JUST DAO forum](https://forum.justlend.org/) before submission. Non-whitelisted proposers must have more than 200 million available WJST; a current whitelist entry bypasses this balance gate, but other proposal checks still apply. After voting, a non-canceled proposal passes the vote gate when For votes exceed Against votes and reach at least 600 million. It must then be queued and wait the 48-hour Timelock delay before execution; neither approval nor the passage of time automatically executes it.

JST tokens enable holders to collectively act as managers of the protocol, enabling them to vote and propose. The process of submitting a proposal and voting is as shown below (before entering the lock phase, you can cancel the created proposal at any time by proposal)

![proposal process](https://raw.githubusercontent.com/justlend/justlend-docs/main/images/proposal.png)

1. Eligible accounts call `propose()` to create proposals. With the observed delay of 1, a proposal created at B remains Pending through B+1; B+2 is the earliest Active block. Read `state(proposalId)` before casting a vote.
2. Voting is token-weighted: **1 JST wrapped as WJST represents 1 whole vote**, not one vote per holder. Voters may vote for, against, or abstain, using available WJST at voting time; the voted weight is locked for the proposal. The voting period lasts for 3 days. After voting is no longer Pending or Active, unlocking votes and withdrawing JST are separate user transactions; see the [governance contract reference](../developers/supply_and_borrow_market/governance.md#available-votes-locks-and-withdrawal).
3. After the voting period ends, a non-canceled proposal becomes Defeated if either vote condition fails, or Succeeded if both pass. A successful proposal must be submitted to `queue()`; it does not automatically trigger the executor.
4. Queueing sets the Timelock execution time. After the 48-hour delay, `execute()` may be called before expiry. The proposal remains Queued until execution or expiry, rather than returning to the initial Pending state.

Including the usual ~2-day forum discussion, the process takes roughly a week. The on-chain voting and Timelock periods total about 5 days, plus the block boundary and any delay before queueing or execution; the forum period is not enforced on-chain.
