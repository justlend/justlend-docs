---
title: Documentation Verification Evidence
description: Dated Mainnet pointer and ABI evidence, original issue closure boundaries, and the limits of node ABI, compiler output and source-derived tuple verification.
---

# Documentation Verification Evidence

## Completion and release status

**The original 34 findings are not all completed.** This recheck, dated **2026-10-14**, covers the original targets, the selected ABI downloads changed in [PR 124](https://github.com/justlend/justlend-docs/pull/124), and their Mainnet address pointers. It is not a whole-contract or frontend security audit.

- **16** original findings have repository-level documentation fixes.
- **11** original targets already contain their correction; they are not new fixes made by this PR.
- **3** remain partial: frontend-linked prepayment acceptance (**JL-024**), hosted whitepaper voting wording (**JL-026**), and complete deployment/ABI artifact coverage (**JL-030**).
- **4** remain unresolved outside this repository: historical dates, tier/boundary wording, zero-factor collateral wording, and the help-center liquidation example (**JL-006–JL-009**).

At recheck, the PR was open and not deployed. The hosted documentation still contains older examples/interfaces, including the former Governor implementation pointer. A repository fix or a successful build is **not** confirmation that the hosted target is fixed. The hosted original-target count is **11 already corrected / 23 not completed end-to-end**. The official PDF additionally retains its page-13 V1 inclusive health boundary; the local review copy is not an online publication.

The [34-item checklist and machine-readable evidence](verification-evidence-20261014.json) separate repository and hosted status. Historical mining rules require the product/content authority; a decision not to edit an announcement is not evidence that its inconsistency was fixed.

## Address verification basis

The source of these pointer corrections is a **read-only Mainnet getter response**, not a guessed address, a branch name, or an assumption that this PR upgraded a contract. `wallet/triggerconstantcontract` returned successful reads for the following calls:

| Role | Read on this contract | Getter | Decoded Mainnet result |
|---|---|---|---|
| Governor implementation | `TEqiF5JbhDPD77yjEfnEMncGRZNDt2uogD` | `implementation()` | `TUeNh9BsYK44XePmFAuKZWg2rJuU7bSt5u` |
| Oracle entrypoint | `TGjYzgCyPobsNS9n6WcbdLVR9dH7mWqFx7` (Comptroller) | `oracle()` | `TGnYnSn4G9PgWFj7QQemh4YMZKp3fkympJ` |
| Oracle backend | `TGnYnSn4G9PgWFj7QQemh4YMZKp3fkympJ` | `v1PriceOracle()` | `TMiNCmvD3zdsv6mk7niBU6NPBzVNjYMQTV` |
| WJST | Governor proxy above | `wjst()` | `TXk9LnTnLN7oH96H3sKxJayMxLxR9M4ZD6` |
| sTRX implementation | `TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5` | `implementation()` | `TUAV6ZSCXtF8KVvDKSeVmAbJEovTBf4HtG` |
| Rental implementation | `TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd` | `implementation()` | `TNoHbPuBQrVanVf9qxUsSvHdB2eDkeDAKD` |
| Market's sTRX caller | Rental proxy above | `strx()` | `TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5` |

These values agree with the earlier 2026-10-12 reads. The Governor **entrypoint remains the proxy**, `TEqiF5JbhDPD77yjEfnEMncGRZNDt2uogD`; only the documentation's implementation pointer changed from `TCiQTkxhzwSeXhRsNdHCvrxHRAvpjQn5Dt`. The Oracle proxy and backend are different roles and need different interfaces.

The main collection ran between node-reported blocks **87,096,574 and 87,096,591**. The calls were **not an atomic, block-pinned snapshot**; each request has its own UTC observation time in the JSON. Additional empty-order/liquidity views were read later and are separately timestamped. Re-read pointers after an upgrade and use the implementation applicable at the historical event block. The targeted recheck does not replace `contracts.json`'s older whole-registry review date or certify Nile/other deployments.

### Reproduce a pointer read

No wallet, private key, signature or broadcast is needed:

```sh
curl --fail --silent --show-error \
  -H 'Content-Type: application/json' \
  https://api.trongrid.io/wallet/triggerconstantcontract \
  --data '{"owner_address":"TEqiF5JbhDPD77yjEfnEMncGRZNDt2uogD","contract_address":"TEqiF5JbhDPD77yjEfnEMncGRZNDt2uogD","function_selector":"implementation()","parameter":"","visible":true}'
```

Require `result.result == true` and a valid `constant_result` word. For an address result, take its last 20 bytes, prepend TRON's `41` prefix, and decode with a TRON address library. The recorded Governor word ends in `ccda938a49c9ab6b0c302d4f7e42126e4821bfad`, corresponding to the new Base58 pointer above. Do not interpret an RPC error or an empty word as an address.

## ABI verification basis

The recheck compares function name/input types, return types, mutability, and event input/indexed layouts. Tuple components are compared when available. Scalar parameter-name changes do not change a selector; omitting a tuple field, changing a return type or changing an event input list does change the integration contract.

**109 selected entries** in **7 interface files** now match the recorded basis. This does not mean every function/event in every deployment is covered.

| Download | Checked entries | Primary basis | Important limit |
|---|---:|---|---|
| `governor-alpha.json` | 23 | `wallet/getcontract` ABI for the current implementation | `getReceipt` component fields use pinned source; node output only says `tuple`. Legacy filename retained. |
| `wjst.json` | 15 | Node ABI at the WJST pointer | Selected wrapping/vote-lock functions/events, not a full governance lifecycle test. |
| `jtrx-repay.json` | 2 | Node ABI at `TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP` | Native repayment subset; not the generic TRC20 interface. |
| `price-oracle.json` | 1 | Node ABI at the Oracle proxy | `getUnderlyingPrice` only; not the backend ABI. |
| `price-oracle-impl.json` | 6 | Node ABI at the `v1PriceOracle()` result | Selected backend methods/event; restricted `setPrice` was not executed. |
| `strx.json` | 39 | Compiler ABI for bytecode-matched STRXG2 | 12 selected functions and all 27 current implementation event declarations; separate admin/historical deployments excluded. |
| `energy-market.json` | 23 | Compiler ABI for bytecode-matched MarketG1 | 19 selected functions and 4 documented events; still not the complete implementation/admin ABI. |

### Node ABI and source-derived fields

A reproducible node ABI read uses:

```sh
curl --fail --silent --show-error \
  -H 'Content-Type: application/json' \
  https://api.trongrid.io/wallet/getcontract \
  --data '{"value":"TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP","visible":true}'
```

The jTRX response defines `repayBorrow(uint256) payable` with no output and `repayBorrowBehalf(address) payable` with no output. The old download already had the self-repayment argument: its correction removes an erroneous `uint256` return and adds the behalf method, not a no-argument repayment replacement. The [official CEther definition](https://github.com/justlend/justlend-protocol/blob/f28f3b462a4f281761e23423554563e15fc9f028/contracts/CEther.sol#L84-L100) supports the semantics, including failure by revert.

The node Governor ABI omits Receipt tuple components. `bool hasVoted / uint8 support / uint96 votes` therefore comes from the fixed [official Receipt definition](https://github.com/justlend/justlend-protocol/blob/f28f3b462a4f281761e23423554563e15fc9f028/contracts/Governance/Bravo/GovernorBravoInterfaces.sol#L149-L158), not from a reproduced deployed compiler artifact. This exception is explicit in the evidence JSON. The [WJST source](https://github.com/justlend/justlend-protocol/blob/f28f3b462a4f281761e23423554563e15fc9f028/contracts/Governance/WJST.sol#L93-L125) supports available-balance voting and explicit unlocking; the full deployed source/compiler bundle and write lifecycle were not reproduced or exercised.

### Compiler and receipt evidence

The Mainnet node reports **no ABI entries** for the current STRXG2 and MarketG1 implementations. Their entries were **not** copied from a nonexistent node ABI. Locally available source was compiled with [TRON Solidity 0.8.18](https://github.com/tronprotocol/solidity/releases/tag/tv_0.8.18), optimizer enabled, 200 runs. The compiler file SHA-256 is `cc258d6b2a77eb19c8092fa3c9d13fd5f658bdc309ef358b5ff0a9c069d5ea6c`.

After excluding **only 53 bytes of trailing Solidity CBOR metadata and its length**, compiled creation bytecode and the node's creation bytecode have equal executable hashes:

| Implementation | Metadata-excluded creation SHA-256 |
|---|---|
| STRXG2 | `bc6e283499d301babde5105027afc52cf928d7fa0d2952cb1601bffc13064fa7` |
| MarketG1 | `1c465c0f1db1d40ae38e9ced76ef7a0e825af1d4cff96ea3cef5a740b0fa0111` |

The full metadata hashes differ. Compiler-input and source-file hashes are recorded, but the source bundle is not published here; this is **not an exact, publicly reproducible deployment build** or a claim of full runtime testing. The [manifest](abis/manifest.json) and evidence distinguish this compiler basis from direct node ABI and source-only tuple evidence.

The committed [settlement fixture](https://github.com/justlend/justlend-docs/blob/ded33496ecf9528d09b70659552d4f488ea242b0/scripts/fixtures/docs-verification/settlement-events.json) also records successful historical `Deposit`, `Withdraw`, `Claim`, and `RentClaimed` receipts. Offline decoding checks input positions, indexed fields, units and decoded values. `RentClaimed` additionally matches the internal TRX transfer to sTRX. No transaction was sent for these checks. The three newly included rental events are compiler-backed; they are not being described as having the same receipt-level cross-check.

## Additional ABI corrections found during this recheck

The earlier tests covered named ABI gaps but did not compare every existing MarketG1 entry. The direct comparison found **five surviving return-definition mismatches** and **two incomplete prose event signatures**, which were then corrected:

| Definition | Previous download/prose | Corrected definition |
|---|---|---|
| `getRentInfo` | Two uint256 returns | Three positional values: uint256, uint256, bool |
| `rentals` | One uint256 named rentBalance | One RentalInfo tuple: amount, securityDeposit, rentIndex |
| `rentPaused` | uint256 | bool |
| `returnResource` | No return; first parameter called renter | uint256 refund; first parameter is receiver |
| `returnResourceByReceiver` | No return | uint256 refund |
| `RentResource` | Omitted final state fields | Includes securityDeposit and rentIndex; now also downloadable |
| `ReturnResource` | Omitted final state fields | Includes securityDeposit and rentIndex; now also downloadable |

`Liquidate` is also included in the selected download to cover its existing documented declaration. The `getRentInfo` bool belongs to the **Energy Rental** reserve check; it must not be substituted for a V1 lending account shortfall. Rental and lending liquidation rules are different domains.

## Other claim-specific evidence

- **Token precision:** ten fresh `decimals()` reads confirm 18 for sTRX, wstUSDT, TUSD, USDJ, USD1, SUN, BTT, JST and HTX, and 6 for WBTT. The JSON includes each Mainnet token address and return word; it does not certify every registry entry or an unrelated same-symbol token.
- **Liquidation:** fresh V1 `closeFactorMantissa()` is `0.5e18`, and `liquidationIncentiveMantissa()` is `1.08e18`. The [Comptroller's selected-market debt check](https://github.com/justlend/justlend-protocol/blob/f28f3b462a4f281761e23423554563e15fc9f028/contracts/Comptroller.sol#L451-L467) supports the per-market close factor. V2 explanatory ratios do not constitute integer-edge transaction testing.
- **API interpretation:** plain and address-query `/lend/jtoken` reads both return 24 markets with jTRX first; the address query does not provide the promised filter. The sampled debt-free account returns `health=0`, while the liquidity view returns error=0/shortfall=0. `/mining/apy` is a jToken/reward-token map, not a flat `apy` field.
- **V2 errors:** five fresh invalid-parameter GETs return HTTP 200, code 202 and `data:null`; they pass the corrected object/null schemas. Success-object required fields and invalid-type controls are preserved.
- **Arithmetic and examples:** fixed-rate sTRX quote controls cover fractional TRX and raw-unit conversion; refund examples are recalculated with Decimal arithmetic. These mocks are not real wallet transactions or approval of historical activity rates.
- **Hosted whitepaper:** the fresh official PDF SHA-256 remains `771c200834f212f45ed4eaeabdc8c7c750e835ff6b3b5ad9c7ba78424f27f537`. Page 15's per-holder wording and page 13's V1 inclusive health boundary remain; V2 strict wording and the page-24 vault overload are already present. Local review corrections are separate from publication.

## Regression and remaining coverage

Run the repository checks described in [README](https://github.com/justlend/justlend-docs/blob/ded33496ecf9528d09b70659552d4f488ea242b0/README.md). The new snapshot regression compares every included ABI entry, checks pointer/decimal consistency, and rejects stale download hashes. It uses the recorded evidence **offline**; it does not silently poll or send transactions in CI. The new regressions are still manually run unless a separate CI change wires them into publishing.

The 2026-10-14 checks passed **19 documentation regressions without skips**, **6 existing mocked API tests**, **5 live read-error response schemas**, strict MkDocs, AI consistency and catalog normalization. The 19 includes the freshly built HTML and download checks; it is not a count of closed product findings.

Remaining gaps include the four external activity/help-center findings, hosted publication, frontend-linked acceptance, exact public source/deployment bundles, source-only Receipt components, historical/Nile/admin-proxy ABIs, full governance write lifecycle and live UX. A passing documentation test does not close these gaps.

## Original issue checklist

The statuses below are for the original finding, not an assertion that the whole surrounding feature is tested. `Repository fixed` still requires a separate release; `Already correct` means the original hosted wording/example was confirmed, not that this PR made that correction.

| ID | Original finding | Repository result | Hosted result | Evidence and limit |
|---|---|---|---|---|
| JL-001 | [Liquidation equality and display rounding](https://docs.justlend.org/getting_started/concepts/liquidations/) | Repository fixed | Release pending | V1 liquidation requires an error-free liquidity result with shortfall > 0; pinned Comptroller source supports the predicate, and the sampled debt-free control returns shortfall=0. Three display-rounding examples are present. The hosted whitepaper V1 health residual is a separate unpublished correction. |
| JL-002 | [Withdrawal liquidity and collateral constraints](https://docs.justlend.org/getting_started/overview/) | Repository fixed | Release pending | Overview no longer promises unconditional redemption; market liquidity and account shortfall constraints are explicit. |
| JL-003 | [Automatic liquidation wording](https://docs.justlend.org/getting_started/overview/) | Already correct | Already correct | Hosted Overview explains the liquidator action rather than automatic execution; transaction timing itself was not tested. |
| JL-004 | [Net APY denominator and net worth](https://support.justlend.org/hc/en-us/articles/43813165783961-Introduction-to-Net-APY-and-Net-Worth) | Outside repository | Already correct | Fresh help-center article uses Total supply as the Net APY denominator and separately defines Net worth; contradictory reverse-income sentence is absent. Frontend metrics are not covered. |
| JL-005 | [Refund examples include an extra 20 TRX](https://support.justlend.org/hc/en-us/articles/31228571004569-What-are-the-rules-for-rent-calculation) | Outside repository | Already correct | Fresh help-center examples use a 140 TRX reserve; six Decimal arithmetic controls give 140,104,80,44,120,84. Historical fee assumptions are not re-approved. |
| JL-006 | [Historical mining announcement dates](https://support.justlend.org/hc/en-us/articles/40624200357017-JustLend-DAO-Launches-USDD-Supply-Mining-Phase-III) | External unresolved | Still open | Both articles retain internal date conflicts. Historical effective dates need the activity/content owner; different activities do not remove each article’s internal conflict. |
| JL-007 | [Mining tier count and 50M boundary](https://support.justlend.org/hc/en-us/articles/53030363719193-JustLend-DAO-Launches-Supply-Mining-Phase-XII) | External unresolved | Still open | All nine articles still describe four levels but list T1/T2/T3; the 50M equality boundary remains ambiguous. Historical rules need product confirmation. |
| JL-008 | [Zero collateral factor and collateralizable wording](https://support.justlend.org/hc/en-us/articles/59218265355545-Announcement-on-Enabling-Supply-and-Borrowing-of-U-Market) | External unresolved | Still open | U and USD1 announcements still use collateralizable wording alongside 0% collateral factor. This is not a claim that the markets cannot supply or borrow. |
| JL-009 | [Per-market liquidation close factor example](https://support.justlend.org/hc/en-us/articles/14318285226137-What-are-the-liquidation-rules) | External still open | Still open | Close factor is 0.5 of selected TRX debt 135 USD: maximum repay 67.5 USD, seize 72.9 USDC, leave 127.1 USDC, risk about 98.06; help-center example still repays 105 USD TRX. |
| JL-010 | [jToken redemption quantity](https://docs.justlend.org/developers/common_pitfalls/) | Repository fixed | Release pending | 100e6 / 1e8 is 1 jToken; redeemUnderlying(100e6) is 100 USDT in a 6-decimal market. |
| JL-011 | [Token decimals](https://docs.justlend.org/developers/common_pitfalls/) | Repository fixed | Release pending | Ten Mainnet decimals() reads match the corrected table; token addresses and return words are recorded below. |
| JL-012 | [Oracle address roles](https://docs.justlend.org/developers/contracts_overview/) | Already correct | Already correct | Original human-facing targets already distinguish proxy and backend. Fresh Comptroller.oracle() and proxy.v1PriceOracle() confirm pointers; additional registry/LLM synchronization still awaits docs release. |
| JL-013 | [sTRX quote precision and fractional input](https://docs.justlend.org/developers/staked_trx/) | Already correct | Already correct | Extracted quoteStake passes four fixed-rate raw-unit controls; SDK decimal conversion and exchangeRate boundary are mocked, not wallet transactions. |
| JL-014 | [Resource return caller](https://docs.justlend.org/developers/energy_rental/) | Already correct | Already correct | Payer path uses msg.sender and receiver; receiver path uses renter and msg.sender. The selected returnResource ABI parameter name is now compiler-aligned. |
| JL-015 | [Rental collection versus cumulative read](https://docs.justlend.org/developers/energy_rental/) | Repository fixed | Release pending | claimRental is an sTRX-only write returning this transfer in sun; rentClaimed is the cumulative read. Bytecode-matched source and historical RentClaimed receipt support the interpretation. |
| JL-016 | [Liquidation incentive versus close factor](https://docs.justlend.org/developers/supply_and_borrow_market/comptroller/) | Already correct | Already correct | Fresh incentive=1.08e18 and close factor=0.5e18 are distinct; the existing Returns definition is already corrected. |
| JL-017 | [Vote signatures and receipt tuple](https://docs.justlend.org/developers/supply_and_borrow_market/governance/) | Repository fixed | Release pending | Selected input/output signatures match the node ABI. Receipt components come from pinned official source, not a reproduced deployment compiler artifact. |
| JL-018 | [Borrow-rate formula variable name](https://docs.justlend.org/developers/supply_and_borrow_market/interest_rate_model/) | Already correct | Already correct | Both Jump Rate branches use borrow_rate; supply_rate is separately defined. |
| JL-019 | [Native TRX and TRC20 repayment](https://docs.justlend.org/developers/supply_and_borrow_market/sbm/) | Repository fixed | Release pending | jTRX ABI has repayBorrow(uint256) payable without a return and repayBorrowBehalf(address) payable; not a no-argument replacement. |
| JL-020 | [Unsupported address market filter](https://docs.justlend.org/documents/aidocs/common_questions/) | Repository fixed | Release pending | Fresh plain and address-query requests both return all 24 markets with jTRX first; client exact-address lookup and failure controls are present. |
| JL-021 | [MCP chain writes versus local configuration](https://docs.justlend.org/documents/aidocs/mcp_tools/) | Repository fixed | Release pending | Nine named tool classes explicitly disclose transaction/sign/broadcast paths; local config and the disabled bridge remain separate. Server code is not changed. |
| JL-022 | [Debt-free health zero](https://docs.justlend.org/developers/apis/) | Repository fixed | Release pending | Fresh public API reports zero debt and health=0; the read-only liquidity query reports error=0/shortfall=0. Docs and YAML use debt-first interpretation. |
| JL-023 | [Supply interest versus mining APY](https://docs.justlend.org/developers/supply_and_borrow_market/sbm/) | Repository fixed | Release pending | Fresh API has supplyRate, no supplyApy; mining response is keyed by jToken then reward token. Text now says miningApy is a local variable, not a literal response field. |
| JL-024 | [Prepayment estimate and frontend acceptance](https://docs.justlend.org/developers/energy_rental/) | Partial | Partial | Both rates, threshold, dynamic fee and integer rounding are covered by documentation controls. Separate frontend review found the factors already present, but acceptance is not complete and the RPC failure path remains outside this PR. |
| JL-025 | [Raw exchange-rate conversion](https://docs.justlend.org/resources/glossary/) | Repository fixed | Release pending | 2e26 with 18-decimal underlying/8-decimal jToken means 0.02 whole tokens; 0.02e18 means 2000000 underlying raw units per whole jToken. |
| JL-026 | [Token-weighted voting and vote locks](https://docs.justlend.org/resources/glossary/) | Partial | Partial | Repository voting-weight/available-balance/explicit unlock explanations are corrected. Official PDF page 15 still has per-holder wording; local review copy is not publication. |
| JL-027 | [Email inbox troubleshooting](https://docs.justlend.org/getting_started/concepts/risks/) | Already correct | Already correct | Fresh Risks page checks inbox/spam/address, not user outbox. Real email delivery is not tested. |
| JL-028 | [V1 multiple-market supply capability](https://docs.justlend.org/getting_started/concepts/SBMV2/) | Already correct | Already correct | Fresh V1/V2 comparison permits multiple simultaneous V1 deposits; actual multi-position UI testing is not required to close the wording defect. |
| JL-029 | [V2 LTV LLTV and risk ratio](https://docs.justlend.org/developers/justlend_v2/) | Repository fixed | Release pending | Text distinguishes LTV > LLTV and risk > 1, with rounded values not an execution predicate. Exact integer-rounding boundary transactions were not tested; the official PDF V2 wording already uses a strict greater-than boundary. |
| JL-030 | [ABI coverage and deployment artifacts](https://docs.justlend.org/developers/abis/) | Partial | Partial | Seven selected interfaces now match 109 node/compiler/source-backed entries after correcting five MarketG1 return definitions and two incomplete prose event signatures. Complete public source/deployment artifacts, admin and historical ABI coverage remain gaps. |
| JL-031 | [Read-only quote uses a write tool](https://docs.justlend.org/getting_started/concepts/energy_rental/) | Repository fixed | Release pending | Unsupported rent_energy --dry-run removed; quote uses calculate_energy_rental_price; no quote helper signs or broadcasts. |
| JL-032 | [Whitepaper mint vault overload](https://justlend.org/docs/justlend_whitepaper_en.pdf) | Outside repository | Already correct | Fresh official PDF hash matches the 2026-10-12 snapshot; second page-24 mint includes address vault. Not a fix made by this PR. |
| JL-033 | [Markdown table enum and regex escaping](https://docs.justlend.org/documents/aidocs/mcp_tools/) | Repository fixed | Release pending | Normalizer preserves enum pipes/regex backslashes and is idempotent; actual generated HTML columns are tested. Hosted catalog still needs release. |
| JL-034 | [V2 null business-error schema](https://docs.justlend.org/developers/apis/justlend_apis.yaml) | Repository fixed | Release pending | Five fresh GET error responses are HTTP200/code202/data:null and pass all five corrected schemas; invalid controls remain rejected. |
