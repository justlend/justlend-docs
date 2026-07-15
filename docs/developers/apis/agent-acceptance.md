---
title: API Agent Acceptance Run
description: End-to-end evidence that an anonymous agent can call the JustLend public API — real recorded responses, contract assertions, and the runnable acceptance script.
---

# API Agent Acceptance Run

This page is the **end-to-end acceptance artifact** for the [JustLend DAO API](../apis.md): proof that an agent with nothing but the docs and an HTTP client can call the API and get responses matching the documented contract ([`justlend_apis.yaml`](justlend_apis.yaml)).

- **What it exercises:** every **anonymous GET** read endpoint (no wallet, no key, no auth) plus the V1 and V2 error contracts.
- **How to reproduce:** from the repo root, run `node scripts/api-acceptance.mjs` (Node ≥ 18, read-only, ~8 GET requests). Exit code `0` means every assertion holds.
- **Status: 8/8 probes passed** on the last run. If a re-run fails, the live service has drifted from the documented contract — update [`apis.md`](../apis.md) and the YAML, and record the new run here.

## Last verified run

```text
JustLend API agent acceptance — 2026-07-15T08:09:17.239Z — base https://openapi.just.network

PASS  V1 market list                             HTTP 200  /lend/jtoken
PASS  V1 sTRX + Energy Rental dashboard          HTTP 200  /lend/strx
PASS  V1 mining APY map                          HTTP 200  /mining/apy
PASS  V1 high-risk account list                  HTTP 200  /justlend/liquidate/highRiskAccountList
PASS  V2 vault list                              HTTP 200  /v2/index/vault/list
PASS  V2 market list                             HTTP 200  /v2/index/market/list
PASS  V1 error contract (unknown path)           HTTP 200  /lend/nonExistentXYZ
PASS  V2 error contract (missing params)         HTTP 200  /v2/vault/position

8/8 endpoint probes passed.
```

## What each probe asserts

| Probe | Endpoint | Key assertions |
|-------|----------|----------------|
| V1 market list | `/lend/jtoken` | HTTP 200; `code: 0`, `message: "SUCCESS"`; `tokenList` ≥ 20 entries; `supplyRate`/`cash`/`exchangeRate` are decimal **strings**; `borrowIndex` is a BigInt-safe integer string; `underlyingDecimal` is a JSON integer. |
| V1 sTRX dashboard | `/lend/strx` | `code: 0`; `stakeInfo.reserves` present as decimal string (key renamed from the historical `reserse`); `stakeInfo.decimal` serialized as the string `"18"`; `rentInfo` prices are decimal strings. |
| V1 mining APY | `/mining/apy` | `code: 0`; one key per market (≥ 20); every value is `{ "USDD": "<decimal string>" }`. |
| V1 high-risk list | `/justlend/liquidate/highRiskAccountList` | `code: 0`; `jtokens` is a plain **object map** (not an array); `updateTime` epoch-ms integer; account entries carry string `risk` / USD fields and integer `liquidateStatusStartTime`. |
| V2 vault list | `/v2/index/vault/list` | HTTP 200; **`code: 200`, `message: "Success"`** (V2 success code); top-level `timestamp`; `allVaults.list` entries have string `tvl`/`apy` and array `tags`/`markets`/`allocations`; user-scoped fields are `null` without `address`. |
| V2 market list | `/v2/index/market/list` | `code: 200`; the key is `allMarkets`; `id` matches `0x…` bytes32; `lltv` is a decimal string; `ltv`/`risk`/`loanAmount` are `null` without `address`. |
| V1 error contract | `/lend/nonExistentXYZ` | **HTTP 200 even for errors**; body `code: 404` with a message; `data` omitted. |
| V2 error contract | `/v2/vault/position` (missing params) | **HTTP 200 even for errors**; body `code ≠ 200` (observed `202`); `data: null`; `timestamp` still present. |

## Recorded real responses (truncated)

Captured 2026-07-15 with plain `curl` — no headers, no auth.

### 1. `GET /lend/jtoken` — first of 24 entries

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "tokenList": [
      {
        "address": "TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP",
        "symbol": "jTRX",
        "underlyingSymbol": "TRX",
        "underlyingAddress": "T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb",
        "underlyingPriceInTrx": "1.000000000000000000000000000",
        "underlyingDecimal": 6,
        "reserveFactor": "0.100000000000000000",
        "collateralFactor": "0.750000000000000000",
        "supplyRate": "0.004196584241280000",
        "borrowRate": "0.047954914361424000",
        "exchangeRate": "0.010582523128618106",
        "cash": "2021157853.515481000000000000",
        "totalBorrows": "217298348.792278000000000000",
        "totalSupply": "211176098544.66409163",
        "reserves": "3680255.247515000000000000",
        "borrowIndex": "1361223278609682980"
      }
    ]
  }
}
```

### 2. `GET /v2/index/market/list` — first of 9 markets (anonymous, so user fields are `null`)

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "userMarketsCount": 0,
    "allMarketsCount": 9,
    "userMarkets": [],
    "allMarkets": [
      {
        "id": "0x8fa76896548f751c9009583976933e6cb355513a180548df5d47b1833d20cb17",
        "ltv": null,
        "lltv": "0.800000000000000000",
        "risk": null,
        "liquidity": "113190.228074",
        "liquidityUsd": "113190.228074000000000000",
        "loanSymbol": "USDT",
        "loanAddress": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
        "loanAmount": null,
        "loanUsd": null,
        "borrowRate": "0.000250508418242629",
        "collateralSymbol": "USDD",
        "collateralAddress": "TXDk8mbtRbXeYuMNS83CfKPaYYT8XWv9Hz",
        "collateralAmount": null,
        "collateralUsd": null,
        "collateralDecimals": 18,
        "tags": []
      }
    ]
  },
  "timestamp": 1784101532797
}
```

### 3. Error contracts — business errors ride on HTTP 200

`GET /lend/nonExistentXYZ` → HTTP **200**:

```json
{ "code": 404, "message": "interface [/lend/nonExistentXYZ] non exist" }
```

`GET /v2/vault/position` (required params missing) → HTTP **200**:

```json
{ "code": 202, "message": "error: Invalid value for field 'address': Invalid format; error: Invalid value for field 'vaultAddress': Invalid format", "data": null, "timestamp": 1784101590046 }
```

## Notes for agents

- Branch on the **body `code`** (`0` = success on V1, `200` on V2), never on the HTTP status ([apis.md §1.6](../apis.md#16-error-responses)).
- Parse all decimal quantities as strings with big-decimal/BigInt ([apis.md §1.3](../apis.md#13-numeric-formats)).
- Account-scoped endpoints (`/lend/account?addresses=…`, `/mining/reward?address=…`, `/mining/distributions?addr=…`, `/v2/*/position`) were also verified with a live wallet during the same session; note the **`addr`** parameter quirk on `/mining/distributions`.
- The script intentionally avoids provoking `429`s; rate-limit behavior is documented in [apis.md §1.7](../apis.md#17-rate-limits-and-retry).
