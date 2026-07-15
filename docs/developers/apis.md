---
title: JustLend DAO API Reference
description: Public read-only REST API at openapi.just.network — V1 markets, account positions, liquidation risk, USDD supply-mining rewards, sTRX staking, Energy Rental, plus JustLend V2 (Moolah) vaults and isolated markets. Authoritative schema is the OpenAPI 3.1 YAML.
---

# JustLend DAO API

Public REST endpoints for querying JustLend DAO protocol state: lending markets, user positions, liquidation risk, USDD supply‑mining rewards, sTRX staking, Energy Rental, and JustLend V2 (Moolah) vaults / isolated markets.

## Contents

This page is the human-readable reference. The [OpenAPI 3.1 YAML](apis/justlend_apis.yaml) is the machine-readable contract — treat the YAML as authoritative if they ever diverge.

- [Quick start](#quick-start) — connectivity check + minimal response example.
- [§1 Conventions](#1-conventions) — response envelope, address format, numeric formats, rate / APY semantics, pagination, error responses, rate limits, versioning.
- [§2 jToken Address Reference](#2-jtoken-address-reference) — the 24-market table with `status: active|legacy` and the programmatic-filter tip.
- [§3 Supply & Borrow Market endpoints](#3-supply-borrow-market) — `/lend/jtoken`, `/lend/account`, `/justlend/liquidate/highRiskAccountList`, plus the V2 (Moolah) read endpoints `/v2/index/vault/list`, `/v2/index/market/list`, `/v2/index/position`, `/v2/vault/position`, `/v2/market/position` (§3.4).
- [§4 USDD Supply Mining](#4-usdd-supply-mining) — `/mining/reward`, `/mining/apy`, `/mining/distributions`.
- [§5 Staked TRX & Energy Rental](#5-staked-trx-energy-rental) — `/lend/strx`, `/lend/strxStake/account`, `/lend/rentResource/account`.
- [§6 Quick reference for AI agents](#6-quick-reference-for-ai-agents) — common end-to-end recipes.
- [§7 Interactive API Explorer](#7-interactive-api-explorer) — embedded Swagger UI.
- [§8 Event-stream and indexing options](#8-event-stream-and-indexing-options) — how to query historical Mint / Borrow / Repay events on TRON.

For gotchas while using these endpoints (USDT-style approve race, decimals mismatch, close-factor cap, etc.), see [Common Pitfalls](common_pitfalls.md). For precise term definitions, see the [Glossary](../resources/glossary.md).

- **Base URL:** `https://openapi.just.network`
- **Method:** All endpoints are `GET`. No authentication.
- **Content‑Type:** `application/json`
- **JSON compliance: Level 2** — uniform `{code, message, data}` envelope on every endpoint ([§1.1](#11-response-envelope)), machine-validatable schemas (typed fields + `required` arrays + `x-unit`/`x-decimals` extensions) in the OpenAPI YAML, and a documented compatibility policy ([§1.8](#18-versioning-and-compatibility)).
- **Machine‑readable spec:** [`justlend_apis.yaml`](./apis/justlend_apis.yaml) (OpenAPI 3.1). Importable into Swagger UI, Postman, Insomnia, or any LLM tool.
- **Live verification:** the endpoints on this page are exercised end-to-end in the [agent acceptance run](apis/agent-acceptance.md) (runnable via `node scripts/api-acceptance.mjs`).
- **Rate limits:** The public service is unauthenticated and may throttle abusive traffic. Keep `pageSize <= 1000`, cache stable metadata such as jToken lists, and retry `429` / `5xx` responses with exponential backoff.

## Quick start

Run this read-only request to verify connectivity and inspect the current JustLend market list:

```bash
curl -sS https://openapi.just.network/lend/jtoken
```

Expected result (one token shown in full — a real response captured 2026-07-15; the live response has 24 entries with the same shape):

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "tokenList": [
      {
        "address":              "TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP",
        "symbol":               "jTRX",
        "underlyingSymbol":     "TRX",
        "underlyingAddress":    "T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb",
        "underlyingPriceInTrx": "1.000000000000000000000000000",
        "underlyingDecimal":    6,
        "reserveFactor":        "0.100000000000000000",
        "collateralFactor":     "0.750000000000000000",
        "supplyRate":           "0.004196584241280000",
        "borrowRate":           "0.047954914361424000",
        "exchangeRate":         "0.010582523128618106",
        "cash":                 "2021157853.515481000000000000",
        "totalBorrows":         "217298348.792278000000000000",
        "totalSupply":          "211176098544.66409163",
        "reserves":             "3680255.247515000000000000",
        "borrowIndex":          "1361223278609682980"
      }
      /* ... 23 more entries ... */
    ]
  }
}
```

**Units cheat-sheet for the response above** (see [§1.3](#13-numeric-formats) and [§1.4](#14-rate-apy-semantics) for the full table):

- **All decimal quantities are JSON strings** — parse with arbitrary-precision decimal/BigInt tooling, never IEEE-754 floats.
- `borrowRate`, `supplyRate`, `collateralFactor`, `reserveFactor` — annualized / fractional **decimals**. Multiply by 100 for percent. (The USDD mining `apy` is served separately by `/mining/apy`, see §4.1.) See [§1.4 Rate / APY semantics](#14-rate-apy-semantics) for the full table.
- `cash`, `totalBorrows`, `reserves` — already de-scaled by the underlying's decimals. Use as-is.
- `totalSupply` — **jToken** units (always 8 decimals).
- `borrowIndex` — cumulative interest index, scaled by `1e18`; exceeds 2^53, so keep it a string/BigInt (see [Glossary → mantissa](../resources/glossary.md#mantissa)).
- `exchangeRate` — **de-scaled** jToken → underlying ratio (human underlying per human jToken), *not* the raw on-chain `1e18` mantissa.

For integrations, import the OpenAPI schema from [`apis/justlend_apis.yaml`](./apis/justlend_apis.yaml), then start with `GET /lend/jtoken` for market metadata and `GET /lend/account?addresses={wallet}` for a user's positions.

---

## 1. Conventions

These conventions apply to **every** response unless an endpoint says otherwise.

### 1.1 Response envelope

Every response — success **and** business error — uses the same `{code, message, data}` envelope. The success `code` differs between the two API generations:

**V1 endpoints** (`/lend/...`, `/mining/...`, `/justlend/...`):

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": { ... }
}
```

**V2 endpoints** (`/v2/...`):

```json
{
  "code": 200,
  "message": "Success",
  "data": { ... },
  "timestamp": 1784101532272
}
```

| Field       | Type    | Meaning                                                                                                       |
|-------------|---------|----------------------------------------------------------------------------------------------------------------|
| `code`      | integer | **V1:** `0` = success. **V2:** `200` = success. Any other value is a business/validation error (see [§1.6](#16-error-responses)). |
| `message`   | string  | `"SUCCESS"` (V1) / `"Success"` (V2) on success, otherwise a short error description.                          |
| `data`      | object  | Endpoint payload. Shape is documented per endpoint below. On business errors it is **absent** (V1) or **`null`** (V2). |
| `timestamp` | integer | **V2 only.** Server time of the response, epoch milliseconds. Always present, including on business errors.   |

> **JSON compliance: Level 2.** Uniform envelope on every endpoint, machine-validatable response schemas (typed fields, `required` arrays, `x-unit` / `x-decimals` / `x-format` extensions) in [`justlend_apis.yaml`](apis/justlend_apis.yaml), and a documented compatibility policy ([§1.8](#18-versioning-and-compatibility)).

> **Field necessity (必返性).** Every field documented for a `data` schema is **always returned** (required) unless it is explicitly marked `nullable` or `optional` — a `nullable` field is still always present but its value may be `null` (e.g. `liquidateStatusStartTime`, or the V2 user-scoped fields when no `address` is supplied). The machine-readable `required` arrays in [`justlend_apis.yaml`](apis/justlend_apis.yaml) enumerate these per schema, so an agent can distinguish "field missing = bug/unexpected" from "value null = documented empty state" and validate responses programmatically. The per-endpoint tables below carry the same information in their **Required** column.

### 1.2 Address format

All addresses are TRON **Base58** addresses (start with `T`, 34 chars). Examples: `TKFRELGGoRgiayhwJTNNLqCNjFoLBh3Mnf`.

### 1.3 Numeric formats

> **All decimal quantities (amounts, rates, prices, indexes) are serialized as JSON *strings*** — on V1 and V2 alike. Parse them with arbitrary-precision decimal / BigInt tooling, never IEEE-754 floats (many values carry more than 15 significant digits; `borrowIndex` and V2 share amounts exceed 2^53). Counts, flags and token decimals are plain JSON integers, with two quirks: `/lend/strx` serializes `decimal` / `underlyingDecimal` as strings (`"18"`, `"6"`), and `/mining/reward` serializes `currPhase` and the status enums as strings.

| Format                | Where it appears                                                                              | How to read it                                                                                        |
|-----------------------|-----------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| Decimal string        | `borrowRate`, `supplyRate`, `apy`, `collateralFactor`, `health`, `risk`, `exchangeRate`, etc. | Already human‑readable. `"0.064673"` means `6.4673 %` for rates, `"0.75"` means `75 %` for factors.   |
| Underlying amount     | `cash`, `totalBorrows`, `reserves`, `supplyBalanceUnderlying`, `borrowBalanceUnderlying`      | Decimal string, already de‑scaled by the asset's decimals. Use as‑is for display.                     |
| jToken amount         | `totalSupply` of `/lend/jtoken`, `supplyBalanceJtoken`                                        | Decimal string in jToken units (jTokens always have **8** decimals on TRON).                          |
| TRX value             | Anything ending in `InTrx`                                                                    | Decimal string, already de‑scaled (TRX has 6 decimals). `"41630.103606"` means 41,630.10 TRX.        |
| USD value             | Anything ending in `Usd`                                                                      | Decimal string, already de‑scaled US dollars.                                                         |
| Mantissa string       | `borrowIndex` of `/lend/jtoken`                                                               | Integer string scaled by `1e18`; exceeds 2^53 — parse as BigInt.                                      |
| Raw share amount      | `shareAmount`, `borrowShares` on V2 position endpoints                                        | Integer string in raw base units; can exceed 2^53 — parse as BigInt.                                  |
| Epoch milliseconds    | `updateTime`, `liquidateStatusStartTime` (high-risk list), V2 `timestamp`                     | Plain JSON integer, Unix epoch in milliseconds.                                                       |
| Hex string            | `amount`, `index`, `merkleIndex`, `merkleRoot`, `proof` in `/mining/distributions`            | Hex‑encoded `uint256`, bare `0x…`. **The leading `:` shown in some legacy examples is a delimiter and is not part of the value.** Pass directly to the on‑chain claim contract. |

The OpenAPI YAML makes the unit and scale machine-readable: amount / rate / price / time fields carry an `x-unit` extension (plus `x-decimals` where the scale is fixed, and `x-format` for hex or non-RFC time layouts).

### 1.4 Rate / APY semantics

> **All `*Rate` and `apy` values are annualized decimals.** Multiply by 100 to get a percentage.

| Field         | Meaning                                                                  | Example value | Display      |
|---------------|--------------------------------------------------------------------------|---------------|--------------|
| `supplyRate`  | Annualized interest a supplier earns (excluding mining rewards).          | `0.00904450`  | `0.90 % APY` |
| `borrowRate`  | Annualized interest a borrower pays.                                      | `0.06467371`  | `6.47 % APY` |
| `apy` (mining)| Annualized USDD mining reward APY paid on top of `supplyRate`.            | `0.09175706`  | `9.18 % APY` |

A user's **total supply APY** in a market that has mining enabled is therefore `supplyRate + apy`.

### 1.5 Pagination

Endpoints that accept `pageNo` and `pageSize` return:

```json
{ "totalCount": 1234, "totalPage": 13, "list": [ ... ] }
```

- `pageNo` is 1‑based. Default = `1`.
- `pageSize` default = `10`, **max = `1000`**.
- Invalid or out-of-range `pageNo`/`pageSize` are often **silently ignored** (defaults applied, `200 SUCCESS`) rather than rejected — validate client-side. See [§1.6 Error responses](#16-error-responses).

### 1.6 Error responses

> **Important for clients and AI agents:** business and validation outcomes are returned with **HTTP `200`** and the same `{ code, message, data }` envelope — **not** signalled through HTTP status codes, and **not** in RFC 7807 form. **Branch on the body `code`, not the HTTP status.** Only transport-level conditions (rate limiting, server faults) surface as non-`200` HTTP statuses.

**V1 business / validation errors — HTTP `200`, `code` ≠ 0, `data` omitted** (real response, captured 2026-07-15):

```json
{ "code": 404, "message": "interface [/lend/nonExistentXYZ] non exist" }
```

**V2 business / validation errors — HTTP `200`, `code` ≠ 200, `data: null`** (real response, captured 2026-07-15):

```json
{ "code": 202, "message": "error: Invalid value for field 'address': Invalid format; error: Invalid value for field 'vaultAddress': Invalid format", "data": null, "timestamp": 1784101590046 }
```

| Signal | How to detect failure |
|--------|------------------------|
| Body `code` | **V1:** `0` = success; any non-zero value (e.g. `1`, `404`) is an error. **V2:** `200` = success; any other value (e.g. `202` = invalid parameters) is an error. Read `message`; `data` is absent (V1) or `null` (V2). |
| HTTP status | `200` for virtually all business/validation outcomes, **including "not found" and invalid parameters**. Do **not** use the HTTP status to detect business errors. |

**Transport-level statuses (the only non-`200` HTTP codes to expect):**

| HTTP status | Meaning | Retry |
|-------------|---------|-------|
| `429` | Too Many Requests — throttled. | Yes — exponential backoff (see §1.7). |
| `5xx` | Server error. | Yes — with backoff. |

**Silent parameter handling (must-know):** unknown or out-of-range query parameters (e.g. `pageSize=invalid`, `pageNo=-1`) are commonly **silently ignored** — the service returns `200 SUCCESS` with default data rather than rejecting the request. Some endpoints do return a non-zero `code` (e.g. `{"code":1,"message":"illegal pageNo or pageSize"}`, or `{"code":1,"message":"Required request parameter 'addr' ... is not present"}` when a required parameter is missing), but **this is not guaranteed**. The API does **not** reliably validate inputs for you: **validate parameters client-side** and never assume a malformed request will fail.

> This error contract reflects the live service as verified on 2026-07-15 (see the [agent acceptance run](apis/agent-acceptance.md)). A future API revision may adopt HTTP status codes and/or a structured error body; until then, treat HTTP `200` + body `code` as authoritative and validate inputs client-side.

### 1.7 Rate limits and retry

The public API is designed for read-only integrations and AI agents. It is not a bulk export interface.

!!! warning "No published numeric rate limit"
    JustLend has not published a contractual req/sec ceiling for `https://openapi.just.network`. The service silently throttles abusive clients with `429` and may queue or refuse excess concurrent connections — but the exact thresholds are not documented and may change without notice. **Do not hard-code a specific req/sec number from this page or anywhere else; discover the limit empirically with an adaptive policy.**

**Adaptive client policy (recommended starting point):**

Start conservative and let the server tell you when to back off:

```text
initial_rate         = 1 req/s
concurrent_max       = 2          # connections in flight
on each clean window (60 s, no 429): double initial_rate, cap at 20 req/s
on 429:
    sleep = base * (2 ** attempt) + random(0, jitter_ms)
    base = 1000 ms, max attempt = 5, max sleep = 30 s
    after 5 failed attempts in a row: halve initial_rate, reset attempt counter
on 5xx (transient):
    same exponential backoff as 429
on persistent 429 across multiple windows:
    treat the current rate as the operator's ceiling and stay below it
```

This policy converges to the real ceiling without ever guessing it. The 20 req/s cap is an arbitrary safety net so a buggy client doesn't spin to 1000 req/s on its own; adjust based on whatever you observe in production.

**General hygiene (works regardless of the actual limit):**

- Use `pageSize <= 1000`; this is the documented maximum for paginated endpoints.
- Cache stable reference data such as jToken addresses, symbols, decimals, and collateral factors (TTL ≥ 5 min is safe; these change only via governance).
- Avoid tight polling loops. Market dashboards normally do not need sub-second refreshes; a 30-second refresh is plenty.
- For per-account health monitoring across many addresses, batch via the high-risk endpoint (`/justlend/liquidate/highRiskAccountList`) rather than polling `/lend/account` per address.
- If you need sustained high-volume traffic, contact the JustLend team before production launch (the public service is unauthenticated and has no per-key tier).

### 1.8 Versioning and compatibility

The OpenAPI `info.version` is the documentation schema version. The HTTP API is read-only and backward-compatible unless an endpoint or field is explicitly marked otherwise.

- Existing fields may be extended with new optional fields. Clients should ignore unknown fields.
- Field removals, type changes, or semantic changes require a documentation version update and deprecation note before rollout.
- The service itself occasionally renames keys without notice — observed examples: `stakeInfo.reserse` (typo) became `reserves`, and the per-account key in `/lend/account` / `/lend/strxStake/account` responses is `address` (older captures showed `addresses`). Where this happened, this page documents the **current** key and notes the historical one; defensive clients may accept both.
- When the rendered page and OpenAPI YAML differ, treat [`apis/justlend_apis.yaml`](./apis/justlend_apis.yaml) as the source of truth for request and response shapes.

---

## 2. jToken Address Reference

Several endpoints key their payloads by jToken address (e.g. `data["TKFRELGGoRgiayhwJTNNLqCNjFoLBh3Mnf"]`). Use this table to translate.

The protocol currently exposes **18 active + 6 legacy = 24 markets**. Legacy markets are closed to new supply and borrow — existing positions remain queryable so they can be unwound, but do not direct new deposits to them.

!!! tip "Programmatic filter"
    For agents that prefer not to parse prose: each entry in [`/developers/contracts.json` → `networks.mainnet.jtokens.<symbol>`](contracts.json) carries an explicit `status` field with value `"active"` or `"legacy"`. Filter `status == "active"` to get the 18 active markets, `status == "legacy"` to get the 6 legacy ones. The schema and enum are documented in [`contracts.schema.json`](contracts.schema.json).

| jToken      | Address                                | Underlying | Notes                                       |
|-------------|----------------------------------------|------------|---------------------------------------------|
| `jTRX`      | `TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP`   | TRX        | Native TRON token                           |
| `jUSDT`     | `TXJgMdjVX5dKiQaUi9QobwNxtSQaFqccvd`   | USDT       | Tether                                      |
| `jUSDD`     | `TKFRELGGoRgiayhwJTNNLqCNjFoLBh3Mnf`   | USDD       | **USDD supply‑mining market** (see §4)      |
| `jUSD1`     | `TBEKggwqFkrc4KckQVR9BLucAmQugafEZf`   | USD1       | World Liberty Financial USD                 |
| `jTUSD`     | `TSXv71Fy5XdL3Rh2QfBoUu3NAaM4sMif8R`   | TUSD       | TrueUSD                                     |
| `jwstUSDT`  | `TD5SdLw5scR6mXgyMK2xKrFJpauDjpKqrW`   | wstUSDT    | Wrapped staked USDT                         |
| `jsTRX`     | `TJQ9rbVe9ei3nNtyGgBL22Fuu2xYjZaLAQ`   | sTRX       | Staked TRX                                  |
| `jBTC`      | `TLeEu311Cbw63BcmMHDgDLu7fnk9fqGcqT`   | BTC        |                                             |
| `jWBTC`     | `TVyvpmaVmz25z2GaXBDDjzLZi5iR5dBzGd`   | WBTC       | Wrapped Bitcoin                             |
| `jETH`      | `TR7BUFRQeq1w5jAZf1FKx85SHuX6PfMqsV`   | ETH        |                                             |
| `jETHB`     | `TWBxQMb6RD3qmkXUXpNwVCYbL8SHNreru6`   | ETHB       | Bridged Ethereum                            |
| `jJST`      | `TWQhCXaWz4eHK4Kd1ErSDHjMFPoPc9czts`   | JST        | JUST                                        |
| `jWIN`      | `TRg6MnpsFXc82ymUPgf5qbj59ibxiEDWvv`   | WIN        |                                             |
| `jNFT`      | `TFpPyDCKvNFgos3g3WVsAqMrdqhB81JXHE`   | NFT        |                                             |
| `jBTT`      | `TUaUHU9Dy8x5yNi1pKnFYqHWojot61Jfto`   | BTT        |                                             |
| `jSUN`      | `TPXDpkg9e3eZzxqxAUyke9S4z4pGJBJw9e`   | SUN        |                                             |
| `jHTX`      | `TDA1mWPyAjTRATMGA55UTswGAHhV2itEXR`   | HTX        | HTX token (underlying `TUPM7K8REVzD2UdV4R5fe5M8XbnR2DdoJ6`) |
| `jU`        | `TMz7vmyqoq4WKDiztrZpjAZPnzE9XgXaK4`   | U          | U token (underlying `TFNirp6PbqYE1ZTtWuCMUKJWLNZkoCoeFJ`, 18 decimals) |
| `jSUNOLD`   | `TGBr8uh9jBVHJhhkwSJvQN2ZAKzVkxDmno`   | SUN (old)  | Legacy, do not deposit new funds            |
| `jBUSDOLD`  | `TLHASseQymmpGQdfAyNjkMXFTJh8nzR2x2`   | BUSD (old) | Legacy                                      |
| `jUSDCOLD`  | `TNSBA6KvSvMoTqQcEgpVK7VhHT3z7wifxy`   | USDC (old) | Legacy                                      |
| `jUSDDOLD`  | `TX7kybeP6UwTBRHLNPYmswFESHfyjm9bAS`   | USDD (old) | Legacy                                      |
| `jUSDJ`     | `TL5x9MtSnDy537FXKx53yAaHRRNdg9TkkA`   | USDJ       | Legacy, closed to new supply/borrow         |
| `jWBTT`     | `TUY54PVeH6WCcYCd6ZXXoBDsHytN9V5PXt`   | WBTT       | Legacy, closed to new supply/borrow         |

---

## 3. Supply & Borrow Market

### 3.1 `GET /lend/jtoken` — List all SBM markets

Returns the on‑chain state of every Supply & Borrow market: rates, total supply/borrow, exchange rates, prices, and collateral factor.

**Parameters:** none.

**Response data** (real response captured 2026-07-15; one of 24 entries shown)

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "tokenList": [
      {
        "address":              "TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP",
        "symbol":               "jTRX",
        "underlyingSymbol":     "TRX",
        "underlyingAddress":    "T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb",
        "underlyingPriceInTrx": "1.000000000000000000000000000",
        "underlyingDecimal":    6,
        "reserveFactor":        "0.100000000000000000",
        "collateralFactor":     "0.750000000000000000",
        "supplyRate":           "0.004196584241280000",
        "borrowRate":           "0.047954914361424000",
        "exchangeRate":         "0.010582523128618106",
        "cash":                 "2021157853.515481000000000000",
        "totalBorrows":         "217298348.792278000000000000",
        "totalSupply":          "211176098544.66409163",
        "reserves":             "3680255.247515000000000000",
        "borrowIndex":          "1361223278609682980"
      }
    ]
  }
}
```

**Field reference**

| Field                  | Type    | Required | Unit / Format            | Description                                                                 |
|------------------------|---------|----------|--------------------------|-----------------------------------------------------------------------------|
| `address`              | string  | Yes      | TRON address             | jToken contract address (the market).                                       |
| `symbol`               | string  | Yes      | text                     | jToken symbol, e.g. `jTRX`, `jUSDD`.                                        |
| `underlyingAddress`    | string  | Yes      | TRON address             | Underlying asset contract address.                                          |
| `underlyingSymbol`     | string  | Yes      | text                     | Underlying asset symbol.                                                    |
| `underlyingDecimal`    | integer | Yes      | count                    | Decimals of the underlying asset.                                           |
| `underlyingPriceInTrx` | string  | Yes      | TRX (decimal string)     | Oracle price of 1 unit of underlying, denominated in TRX.                   |
| `borrowIndex`          | string  | Yes      | integer string, scaled 1e18 | Cumulative borrow interest index. Exceeds 2^53 — parse as BigInt.        |
| `borrowRate`           | string  | Yes      | annualized decimal string| Borrow APY. `"0.0479"` = `4.79 %`.                                          |
| `supplyRate`           | string  | Yes      | annualized decimal string| Supply APY (excluding mining).                                              |
| `cash`                 | string  | Yes      | underlying units         | Available underlying liquidity in the market. Decimal string.               |
| `reserves`             | string  | Yes      | underlying units         | Protocol reserves in the market. Decimal string.                            |
| `totalBorrows`         | string  | Yes      | underlying units         | Total outstanding debt. Decimal string.                                     |
| `totalSupply`          | string  | Yes      | jToken units (8 decimals)| Total minted jTokens. Decimal string.                                       |
| `exchangeRate`         | string  | Yes      | underlying per jToken    | Current jToken → underlying conversion ratio, de-scaled (not the raw 1e18 mantissa). |
| `collateralFactor`     | string  | Yes      | decimal (0–1)            | LTV cap when used as collateral. `"0.75"` = `75 %`.                         |
| `reserveFactor`        | string  | Yes      | decimal (0–1)            | Share of borrow interest taken as protocol reserve.                         |

---

### 3.2 `GET /lend/account` — User SBM positions

Returns each queried wallet's supply/borrow positions, health factor and totals.

**Parameters**

| Name                  | In    | Type    | Required | Description                                                                   |
|-----------------------|-------|---------|----------|-------------------------------------------------------------------------------|
| `addresses`           | query | string  | yes      | One or more TRON addresses, **comma‑separated** (no spaces).                  |
| `minBorrowValueInTrx` | query | number  | no       | Only return accounts whose total borrow value (in TRX) is ≥ this threshold.   |
| `maxHealth`           | query | number  | no       | Only return accounts whose health is ≤ this threshold (useful to find risky). |
| `pageNo`              | query | integer | no       | 1‑based page number. Default `1`.                                             |
| `pageSize`            | query | integer | no       | Page size. Default `10`, max `1000`.                                          |

**Example request**

```http
GET /lend/account?addresses=T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb,TXJgM...&pageNo=1&pageSize=20
```

**Response data** (real response captured 2026-07-15)

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "totalPage": 1,
    "totalCount": 1,
    "list": [
      {
        "address":                   "TB2e78zyzMnaNG2GRazazmbVVv3J564YHg",
        "health":                    "1.00000595",
        "totalBorrowValueInTrx":     "41630.103606",
        "totalCollateralValueInTrx": "41630.351383",
        "liquidateStatusStartTime":  null,
        "tokens": [
          {
            "address":                "TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP",
            "underlyingSymbol":       "TRX",
            "entered":                1,
            "borrowBalanceUnderlying":"41630.103606391458272468557875",
            "supplyBalanceUnderlying":"55507.13517729334283172067476560",
            "supplyBalanceJtoken":    "5245170.10164455"
          }
        ]
      }
    ]
  }
}
```

**Field reference**

| Field                       | Type    | Required | Unit              | Description                                                                          |
|-----------------------------|---------|----------|-------------------|--------------------------------------------------------------------------------------|
| `address`                   | string  | Yes      | TRON address      | Wallet address. (Earlier versions of this page showed the key as `addresses`; the service returns `address`.) |
| `health`                    | string  | Yes      | ratio (decimal string) | Health factor. `> 1` healthy, `≤ 1` liquidatable. `"5.88"` = very safe.         |
| `totalCollateralValueInTrx` | string  | Yes      | TRX               | Sum of collateral value (after `collateralFactor`). Decimal string.                  |
| `totalBorrowValueInTrx`     | string  | Yes      | TRX               | Sum of outstanding borrow value. Decimal string.                                     |
| `liquidateStatusStartTime`  | string\|null | Yes (nullable) | timestamp | Timestamp when this account first entered a liquidatable state, or `null` if it is not currently flagged. Always present. |
| `tokens[].address`          | string  | Yes      | TRON address      | jToken address of this position.                                                     |
| `tokens[].underlyingSymbol` | string  | Yes      | text              | Underlying symbol, e.g. `USDD`.                                                      |
| `tokens[].entered`          | integer | Yes      | 0 / 1             | `1` if the user has entered this market as collateral, `0` otherwise.                |
| `tokens[].supplyBalanceJtoken`     | string | Yes | jToken units (8d)| Supplied balance in jTokens. Decimal string.                                         |
| `tokens[].supplyBalanceUnderlying` | string | Yes | underlying       | Supplied balance in underlying. Decimal string.                                      |
| `tokens[].borrowBalanceUnderlying` | string | Yes | underlying       | Outstanding borrow in underlying. Decimal string.                                    |

---

### 3.3 `GET /justlend/liquidate/highRiskAccountList` — High‑risk accounts

Returns accounts that are currently liquidatable or close to it. Use this to drive liquidation bots.

**Parameters:** none.

**Response data** (real response captured 2026-07-15; `jtokens` truncated to 2 of 24 keys, `accounts` to 1 of 85 entries)

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "jtokens": {
      "jTRX":  "TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP",
      "jUSDD": "TKFRELGGoRgiayhwJTNNLqCNjFoLBh3Mnf"
      /* ... one key per market, 24 total ... */
    },
    "updateTime": 1784101473987,
    "accounts": [
      {
        "borrower":                "TB2e78zyzMnaNG2GRazazmbVVv3J564YHg",
        "collateralTokenList": [
          {
            "jtokenAddress":    "TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP",
            "amount":           "5245170.10164455",
            "price":            "0.003436452181842813",
            "valueUsd":         "18024.776240",
            "symbol":           "jTRX",
            "exchangeRate":     "0.010582523217337573",
            "collateralFactor": "0.750000000000000000"
          }
        ],
        "borrowTokenList": [
          {
            "tokenAddress":     "T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb",
            "amount":           "41630.094680465196950370956875",
            "price":            "0.324729000000000000",
            "valueUsd":         "13518.499015",
            "symbol":           "TRX",
            "exchangeRate":     "0.010582523217337573",
            "collateralFactor": "0.750000000000000000"
          }
        ],
        "totalCollateralUsd":      "18024.776240",
        "totalBorrowUsd":          "13518.499015",
        "risk":                    "0.999994",
        "liquidateStatusStartTime": 0
      }
    ]
  }
}
```

> **Note:** `jtokens` is a plain JSON **object** (symbol → address map). Older revisions of this page showed it wrapped in a one-element array — that was a documentation error.

**Field reference**

| Field                                 | Type    | Required | Unit                | Description                                                                                |
|---------------------------------------|---------|----------|---------------------|--------------------------------------------------------------------------------------------|
| `updateTime`                          | integer | Yes      | epoch ms            | When the snapshot was computed.                                                            |
| `jtokens`                             | object  | Yes      | symbol → address    | jToken symbol‑to‑address lookup map. Same data as §2.                                      |
| `accounts[].borrower`                 | string  | Yes      | TRON address        | Borrower wallet.                                                                           |
| `accounts[].risk`                     | string  | Yes      | ratio               | **Higher = riskier.** `> 1` means the account is liquidatable now.                          |
| `accounts[].totalCollateralUsd`       | string  | Yes      | USD                 | Total collateral value.                                                                    |
| `accounts[].totalBorrowUsd`           | string  | Yes      | USD                 | Total borrow value.                                                                        |
| `accounts[].liquidateStatusStartTime` | integer | Yes      | epoch ms            | When the account first became liquidatable. `0` = not yet in liquidatable status.          |
| `accounts[].collateralTokenList[]`    | array   | Yes      | object              | One entry per collateral position (see below).                                             |
| `accounts[].borrowTokenList[]`        | array   | Yes      | object              | One entry per borrow position (see below).                                                 |
| `collateralTokenList[].jtokenAddress` | string  | Yes      | TRON address        | jToken address of the collateral.                                                          |
| `collateralTokenList[].symbol`        | string  | Yes      | text                | jToken symbol.                                                                             |
| `collateralTokenList[].amount`        | string  | Yes      | jToken units (8d)   | Amount of jTokens held as collateral.                                                      |
| `collateralTokenList[].price`         | string  | Yes      | USD                 | Current price of the **jToken** in USD (already multiplied by `exchangeRate`).             |
| `collateralTokenList[].valueUsd`      | string  | Yes      | USD                 | `amount × price`.                                                                          |
| `collateralTokenList[].exchangeRate`  | string  | Yes      | underlying / jToken | jToken → underlying conversion ratio.                                                      |
| `collateralTokenList[].collateralFactor` | string | Yes    | decimal (0–1)       | Collateral factor applied for risk calculation.                                            |
| `borrowTokenList[].tokenAddress`      | string  | Yes      | TRON address        | **Underlying** asset address (note: this list keys by underlying, not jToken).             |
| `borrowTokenList[].symbol`            | string  | Yes      | text                | Underlying asset symbol.                                                                   |
| `borrowTokenList[].amount`            | string  | Yes      | underlying          | Outstanding borrowed amount of underlying.                                                 |
| `borrowTokenList[].price`             | string  | Yes      | USD                 | Underlying asset price.                                                                    |
| `borrowTokenList[].valueUsd`          | string  | Yes      | USD                 | `amount × price`.                                                                          |
| `borrowTokenList[].exchangeRate`      | string  | Yes      | underlying / jToken | Exchange rate of the corresponding market.                                                 |
| `borrowTokenList[].collateralFactor`  | string  | Yes      | decimal (0–1)       | Collateral factor of the corresponding market.                                             |

---

### 3.4 JustLend V2 (Moolah) read endpoints

JustLend V2 ("Moolah", Morpho-style architecture — see [JustLend V2](justlend_v2.md)) exposes **ERC-4626 vaults** (passive supply, allocated across markets) and **isolated markets** (one collateral / one loan token pair, identified by a 32-byte hex `id`). Five anonymous read endpoints cover them.

**V2 conventions (differ from V1 — see [§1.1](#11-response-envelope) / [§1.6](#16-error-responses)):**

- Success is `code: 200` with `message: "Success"` (V1 uses `code: 0` / `"SUCCESS"`).
- Business errors are still HTTP `200`, with `code ≠ 200` (e.g. `202` = invalid parameters) and `data: null`.
- Every response carries a top-level `timestamp` (epoch ms).
- All decimal quantities are strings; `shareAmount` / `borrowShares` are raw base-unit integer strings that can exceed 2^53 (use BigInt).
- User-scoped fields (`ltv`, `risk`, `loanAmount`, `userSupplyUsd`, …) are `null` when no `address` is supplied or the user has no position.

#### 3.4.1 `GET /v2/index/vault/list` — All V2 vaults

Returns every V2 vault (name, asset, TVL, APY, performance fee, eligible collateral, underlying market allocations), plus the user's vaults when `address` is given.

**Parameters**

| Name           | In    | Type    | Required | Description                                                             |
|----------------|-------|---------|----------|-------------------------------------------------------------------------|
| `address`      | query | string  | no       | Wallet address; adds the user's vault list (`userVaults`).              |
| `sort`         | query | string  | no       | Sort field: `tvl` or `apy`. Default `tvl`.                              |
| `order`        | query | string  | no       | `desc` or `asc`. Default `desc`.                                        |
| `deposit`      | query | string  | no       | Filter by deposit token symbols, comma-separated (OR condition).        |
| `collateral`   | query | string  | no       | Filter by collateral token symbols, comma-separated (OR condition).     |
| `keyword`      | query | string  | no       | Partial match against vault names and collateral token symbols.         |
| `userPage`     | query | integer | no       | Page number of the user's vault list. Default `1`.                      |
| `userPageSize` | query | integer | no       | Page size of the user's vault list. Default `20`.                       |
| `allPage`      | query | integer | no       | Page number of the full vault list. Default `1`.                        |
| `allPageSize`  | query | integer | no       | Page size of the full vault list. Default `20`.                         |

**Response data** (real response captured 2026-07-15, heavily truncated — full sub-schemas in the [YAML](apis/justlend_apis.yaml))

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "userVaults": { "totalCount": 0, "list": [] },
    "allVaults": {
      "totalCount": 3,
      "list": [
        {
          "chain":             "tron",
          "vaultAddress":      "TXejU9jmd1ooQyY3Zmpo15yN7MjSFYUESg",
          "vaultName":         "JustLend USDT Vault",
          "vaultSymbol":       "jUSDTv2",
          "icon":              "https://static.tronscan.org/production/logo/usdtlogo.png",
          "tags":              [],
          "assetAddress":      "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
          "assetSymbol":       "USDT",
          "assetName":         "Tether USD",
          "assetDecimals":     6,
          "assetIcon":         "https://static.tronscan.org/production/logo/usdtlogo.png",
          "totalSupplyAmount": "413328.006113",
          "tvl":               "413328.006113000000000000",
          "apy":               "0.000711770302729251",
          "performanceFee":    "10.00",
          "collateralTokens":  [ { "address": "TNUC9Qb1rRpS5CbWLmNMxXBjyFoydXjWFR", "symbol": "WTRX", "name": "Wrapped TRX", "decimals": 6, "icon": "…" } /* ... */ ],
          "markets":           [ { "id": "0x8fa76896548f751c9009583976933e6cb355513a180548df5d47b1833d20cb17", "collateralSymbol": "USDD", "totalSupplyAssets": "113259.328861", "borrowSymbol": "USDT", "...": "..." } /* ... */ ],
          "userSupplyUsd":     null,
          "userSupplyAmount":  null,
          "allocations":       [ { "marketId": "0x8fa768…", "collateralSymbol": "USDD", "amount": "113259.286496", "percentage": "27.401793449548277509", "supplyQueueIndex": 0, "isNew": 0, "noMoreAllocation": false } /* ... */ ]
        }
        /* ... 2 more vaults ... */
      ]
    },
    "depositTokens":    [ { "address": "…", "symbol": "USDT", "name": "Tether USD", "decimals": 6, "icon": "…" } /* ... */ ],
    "collateralTokens": [ { "address": "…", "symbol": "WTRX", "name": "Wrapped TRX", "decimals": 6, "icon": "…" } /* ... */ ]
  },
  "timestamp": 1784101532272
}
```

**Field reference (vault entry)**

| Field               | Type          | Required | Unit                 | Description                                                              |
|---------------------|---------------|----------|----------------------|---------------------------------------------------------------------------|
| `chain`             | string        | Yes      | text                 | Chain identifier (`tron`).                                               |
| `vaultAddress`      | string        | Yes      | TRON address         | Vault contract address.                                                  |
| `vaultName` / `vaultSymbol` / `icon` / `tags` | string / array | Yes | text  | Vault display metadata (`tags` is an array of strings).                  |
| `assetAddress` / `assetSymbol` / `assetName` / `assetDecimals` / `assetIcon` | string / integer | Yes | token metadata | The vault's underlying (deposit) asset.       |
| `totalSupplyAmount` | string        | Yes      | asset units          | Total vault supply, de-scaled. Decimal string.                           |
| `tvl`               | string        | Yes      | USD                  | Total value locked. Decimal string.                                      |
| `apy`               | string        | Yes      | annualized decimal   | Vault APY. Decimal string.                                               |
| `performanceFee`    | string        | Yes      | percent (0–100)      | Performance fee; `"10.00"` = 10 %.                                       |
| `collateralTokens[]`| array         | Yes      | token metadata       | Tokens eligible as collateral in this vault's markets.                   |
| `markets[]`         | array         | Yes      | object               | The isolated markets this vault allocates into (ids, per-market supply/borrow totals — full schema in the YAML). |
| `userSupplyUsd`     | string\|null  | Yes (nullable) | USD            | User supply in USD; `null` without `address` / position.                 |
| `userSupplyAmount`  | string\|null  | Yes (nullable) | asset units    | User supply, de-scaled; `null` without `address` / position.             |
| `userSupplyYield`   | string        | No       | asset units          | User supply earnings. Only present in user-scoped responses.             |
| `allocations[]`     | array         | Yes      | object               | Current allocation per market (`amount`, `amountInUsd`, `percentage`, `supplyQueueIndex`, `isNew`, `noMoreAllocation`). |

#### 3.4.2 `GET /v2/index/market/list` — All V2 isolated markets

Returns every V2 isolated market (loan/collateral pair, LLTV, liquidity, borrow rate), plus the user's markets when `address` is given. Accepts the same query parameters as §3.4.1 (`address`, `sort`, `order`, `deposit`, `collateral`, `keyword`, `userPage`, `userPageSize`, `allPage`, `allPageSize`).

**Response data** (real response captured 2026-07-15, truncated to one of 9 markets)

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "userMarketsCount": 0,
    "allMarketsCount":  9,
    "userMarkets":      [],
    "allMarkets": [
      {
        "id":                 "0x8fa76896548f751c9009583976933e6cb355513a180548df5d47b1833d20cb17",
        "ltv":                null,
        "lltv":               "0.800000000000000000",
        "risk":               null,
        "liquidity":          "113190.228074",
        "liquidityUsd":       "113190.228074000000000000",
        "loanSymbol":         "USDT",
        "loanAddress":        "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
        "loanAmount":         null,
        "loanUsd":            null,
        "loanIcon":           "https://static.tronscan.org/production/logo/usdtlogo.png",
        "borrowRate":         "0.000250508418242629",
        "collateralSymbol":   "USDD",
        "collateralAddress":  "TXDk8mbtRbXeYuMNS83CfKPaYYT8XWv9Hz",
        "collateralAmount":   null,
        "collateralUsd":      null,
        "collateralDecimals": 18,
        "collateralIcon":     "https://static.tronscan.org/production/upload/logo/new/TXDk8mbtRbXeYuMNS83CfKPaYYT8XWv9Hz.png",
        "tags":               []
      }
      /* ... 8 more markets ... */
    ]
  },
  "timestamp": 1784101532797
}
```

**Field reference (market entry)**

| Field                | Type         | Required | Unit               | Description                                                            |
|----------------------|--------------|----------|--------------------|-------------------------------------------------------------------------|
| `id`                 | string       | Yes      | hex bytes32        | Market ID. Pass it to `/v2/market/position` as `market`.               |
| `ltv`                | string\|null | Yes (nullable) | decimal (0–1) | User loan-to-value (`loanUsd / collateralUsd`); `null` without position. |
| `lltv`               | string       | Yes      | decimal (0–1)      | Liquidation threshold (liquidation LTV).                                |
| `risk`               | string\|null | Yes (nullable) | ratio        | User risk (`ltv / lltv`); `null` without position.                      |
| `liquidity`          | string       | Yes      | loan token units   | Available liquidity, de-scaled. Decimal string.                         |
| `liquidityUsd`       | string       | Yes      | USD                | Liquidity in USD. Decimal string.                                       |
| `loanSymbol` / `loanAddress` / `loanIcon` | string | Yes | token metadata | The loan (borrowable) token.                                     |
| `loanAmount`         | string\|null | Yes (nullable) | loan token units | User borrowed amount; `null` without position.                    |
| `loanUsd`            | string\|null | Yes (nullable) | USD          | User borrowed value; `null` without position.                           |
| `borrowRate`         | string       | Yes      | annualized decimal | Borrow rate. Decimal string.                                            |
| `collateralSymbol` / `collateralAddress` / `collateralDecimals` / `collateralIcon` | string / integer | Yes | token metadata | The collateral token. |
| `collateralAmount`   | string\|null | Yes (nullable) | collateral units | User collateral amount; `null` without position.                  |
| `collateralUsd`      | string\|null | Yes (nullable) | USD          | User collateral value; `null` without position.                         |
| `tags`               | array        | Yes      | strings            | Market tags.                                                            |

#### 3.4.3 `GET /v2/index/position` — User V2 portfolio summary

Aggregated V2 position for one wallet: totals, net rates, mining rewards, and the per-vault / per-market breakdown.

**Parameters**

| Name      | In    | Type   | Required | Description                  |
|-----------|-------|--------|----------|------------------------------|
| `address` | query | string | yes      | Single TRON wallet address.  |

**Example request**

```http
GET /v2/index/position?address=TB2e78zyzMnaNG2GRazazmbVVv3J564YHg
```

**Response data** (real response captured 2026-07-15 — this wallet has no V2 positions, so totals are zero and the breakdown arrays are empty)

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "totalBorrowUsd":        "0.000000000000000000",
    "totalCollateralUsd":    "0.000000000000000000",
    "totalSupplyUsd":        "0",
    "netEarnApy":            "0",
    "netBorrowRate":         "0",
    "dailyRevenue":          "0.000000000000000000",
    "dailyMiningReward":     "0.000000000000000000",
    "dailyMiningRewardUsdd": "0.000000000000000000",
    "dailyMiningRewardTrx":  "0.000000",
    "collateralCount":       0,
    "markets":               [],
    "vaults":                [],
    "borrowNew":             true,
    "vaultNew":              true
  },
  "timestamp": 1784101588616
}
```

**Field reference**

| Field                   | Type    | Required | Unit               | Description                                                                          |
|-------------------------|---------|----------|--------------------|----------------------------------------------------------------------------------------|
| `totalBorrowUsd`        | string  | Yes      | USD                | Total borrowed value across all V2 markets. Decimal string.                          |
| `totalCollateralUsd`    | string  | Yes      | USD                | Total collateral value across all V2 markets. Decimal string.                        |
| `totalSupplyUsd`        | string  | Yes      | USD                | Total supplied value across all V2 vaults. Decimal string.                           |
| `netEarnApy`            | string  | Yes      | annualized decimal | Weighted-average APY over the user's vault deposits. Decimal string.                 |
| `netBorrowRate`         | string  | Yes      | annualized decimal | Weighted-average borrow rate over the user's loans. Decimal string.                  |
| `dailyRevenue`          | string  | Yes      | USD                | Daily earnings from supplied assets. Decimal string.                                 |
| `dailyMiningReward`     | string  | Yes      | USD                | Daily mining reward (USD value). Decimal string.                                     |
| `dailyMiningRewardUsdd` | string  | Yes      | USDD               | Daily mining reward in USDD. Decimal string.                                         |
| `dailyMiningRewardTrx`  | string  | Yes      | TRX                | Daily mining reward in TRX. Decimal string.                                          |
| `collateralCount`       | integer | Yes      | count              | Number of markets where the user has collateral > 0.                                 |
| `markets[]`             | array   | Yes      | object             | Per-market breakdown: `marketId` (hex string), `health`, `collateralUsd`, `borrowUsd` (decimal strings). |
| `vaults[]`              | array   | Yes      | object             | Per-vault breakdown: `vaultAddress`, `supplyUsd` (decimal string).                   |
| `vaultNew`              | boolean | Yes      | flag               | `true` if the user is a new V2 vault user.                                           |
| `borrowNew`             | boolean | Yes      | flag               | `true` if the user is a new V2 market user.                                          |

#### 3.4.4 `GET /v2/vault/position` — User position in one vault

**Parameters**

| Name           | In    | Type   | Required | Description                        |
|----------------|-------|--------|----------|------------------------------------|
| `vaultAddress` | query | string | yes      | Vault contract address (see §3.4.1). |
| `address`      | query | string | yes      | Single TRON wallet address.        |

**Example request**

```http
GET /v2/vault/position?vaultAddress=TXejU9jmd1ooQyY3Zmpo15yN7MjSFYUESg&address=TB2e78zyzMnaNG2GRazazmbVVv3J564YHg
```

**Response data** (real response captured 2026-07-15 — wallet without a position in this vault; `apy` is still the live vault APY)

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "shareAmount":             "0",
    "depositAmount":           "0.000000",
    "depositUsd":              "0.000000000000000000",
    "apy":                     "0.000711758741868661",
    "dailyInterest":           "0.000000000000000000",
    "dailyInterestAmount":     "0.000000",
    "farmRewardUsddAmount24h": "0",
    "farmRewardTrxAmount24h":  "0"
  },
  "timestamp": 1784101589078
}
```

**Field reference**

| Field                     | Type   | Required | Unit               | Description                                                                     |
|---------------------------|--------|----------|--------------------|----------------------------------------------------------------------------------|
| `shareAmount`             | string | Yes      | raw share units    | Vault shares held by the user. Integer string; can exceed 2^53 — use BigInt.    |
| `depositAmount`           | string | Yes      | asset units        | Deposited amount, de-scaled. Decimal string.                                    |
| `depositUsd`              | string | Yes      | USD                | USD value of the deposit. Decimal string.                                       |
| `apy`                     | string | Yes      | annualized decimal | Vault APY. Decimal string.                                                      |
| `dailyInterest`           | string | Yes      | USD                | Estimated daily interest earnings (USD value). Decimal string.                  |
| `dailyInterestAmount`     | string | Yes      | asset units        | Estimated daily interest earnings in the vault asset. Decimal string.           |
| `farmRewardUsddAmount24h` | string | Yes      | USDD               | Farm rewards over the last 24 h in USDD. Decimal string.                        |
| `farmRewardTrxAmount24h`  | string | Yes      | TRX                | Farm rewards over the last 24 h in TRX. Decimal string.                         |

#### 3.4.5 `GET /v2/market/position` — User position in one market

**Parameters**

| Name      | In    | Type   | Required | Description                                             |
|-----------|-------|--------|----------|---------------------------------------------------------|
| `market`  | query | string | yes      | V2 market id (`0x…` 32-byte hex string, see §3.4.2).    |
| `address` | query | string | yes      | Single TRON wallet address.                             |

**Example request**

```http
GET /v2/market/position?market=0x8fa76896548f751c9009583976933e6cb355513a180548df5d47b1833d20cb17&address=TB2e78zyzMnaNG2GRazazmbVVv3J564YHg
```

**Response data** (real response captured 2026-07-15 — wallet without a position in this market; token metadata, `lltv` and `borrowApy` are live market values)

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "borrowAddress":     "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",
    "borrowSymbol":      "USDT",
    "borrowAmount":      "0",
    "borrowShares":      "0",
    "borrowUsd":         "0.000000000000000000",
    "collateralAddress": "TXDk8mbtRbXeYuMNS83CfKPaYYT8XWv9Hz",
    "collateralSymbol":  "USDD",
    "collateralUsd":     "0.000000000000000000",
    "collateralAmount":  "0",
    "borrowApy":         "0.000250508418242629",
    "ltv":               "0.000000000000000000",
    "lltv":              "0.800000000000000000",
    "risk":              "0.000000000000000000",
    "dailyInterest":     "0"
  },
  "timestamp": 1784101589588
}
```

**Field reference**

| Field               | Type    | Required | Unit               | Description                                                                 |
|---------------------|---------|----------|--------------------|------------------------------------------------------------------------------|
| `borrowAddress`     | string  | Yes      | TRON address       | Loan token contract address.                                                |
| `borrowSymbol`      | string  | Yes      | text               | Loan token symbol.                                                          |
| `borrowAmount`      | string  | Yes      | loan token units   | Borrowed amount, de-scaled. Decimal string.                                 |
| `borrowShares`      | string  | Yes      | raw share units    | Borrow shares. Integer string; can exceed 2^53 — use BigInt.                |
| `borrowUsd`         | string  | Yes      | USD                | Borrowed value. Decimal string.                                             |
| `collateralAddress` | string  | Yes      | TRON address       | Collateral token contract address.                                          |
| `collateralSymbol`  | string  | Yes      | text               | Collateral token symbol.                                                    |
| `collateralAmount`  | string  | Yes      | collateral units   | Collateral supplied, de-scaled. Decimal string.                             |
| `collateralUsd`     | string  | Yes      | USD                | Collateral value. Decimal string.                                           |
| `ltv`               | string  | Yes      | decimal (0–1)      | Loan-to-value ratio. Decimal string.                                        |
| `lltv`              | string  | Yes      | decimal (0–1)      | Liquidation threshold. Decimal string.                                      |
| `borrowApy`         | string  | Yes      | annualized decimal | Borrow APY. Decimal string.                                                 |
| `dailyInterest`     | string  | Yes      | USD                | Daily interest owed. Decimal string.                                        |
| `risk`              | string  | Yes      | ratio              | Risk ratio (`ltv / lltv`). Decimal string.                                  |
| `displayDecimal`    | integer | No       | count              | Display decimals for token amounts. Not returned by every response.        |

---

## 4. USDD Supply Mining

JustLend rewards users who **supply into the USDD market (`jUSDD = TKFRELGGoRgiayhwJTNNLqCNjFoLBh3Mnf`)** with extra USDD. Rewards are distributed in time‑bounded **phases (cycles)**; each phase publishes a Merkle root, and users claim by submitting their `(index, amount, proof)` to the on‑chain claim contract.

> **Reward = supplied‑USDD × `apy` × time_in_phase**. Once a phase ends, the API exposes per‑user Merkle proofs the user submits on‑chain to claim accrued USDD.

| Concept             | Meaning                                                                                                 |
|---------------------|---------------------------------------------------------------------------------------------------------|
| **Phase / Cycle**   | A reward window with a fixed `start` and `end` time. `currPhase` is the phase that is in progress now.  |
| **Phase status**    | `0` = not started · `1` = ongoing · `2` = ended (finalized, claimable) · `3` = paused.                  |
| **Mining APY**      | Annualized USDD bonus paid on top of the underlying market `supplyRate`. Decimal, e.g. `0.0917` = 9.17 %.|
| **Claim**           | After a phase ends, users submit `(merkleIndex, index, amount, proof, merkleRoot)` on‑chain to receive USDD.|
| **Markets covered** | Currently only jUSDD. New markets may be added in the future.                                           |

### 4.1 `GET /mining/apy` — Mining APY per market

Returns the current USDD mining APY for every market that has supply‑mining enabled.

**Parameters:** none.

**Response data** (real response captured 2026-07-15, truncated to 2 of 24 market keys)

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "TKFRELGGoRgiayhwJTNNLqCNjFoLBh3Mnf": {
      "USDD": "0.04275429"
    },
    "TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP": {
      "USDD": "0.00000000"
    }
    /* ... one key per market, 24 total ... */
  }
}
```

**Field reference**

| Field            | Type    | Required | Unit                | Description                                                                                       |
|------------------|---------|----------|---------------------|---------------------------------------------------------------------------------------------------|
| key (top‑level)  | string  | —        | jToken address      | The market the reward applies to. Look up in §2 (here `TKFREL…` is `jUSDD`). The service currently returns **every** market. |
| `USDD`           | string  | Yes      | annualized decimal  | USDD mining APY paid to suppliers of this market, on top of `supplyRate`. Decimal string; `"0.04275429"` = **4.28 % APY**. |

> A market with `"0.00000000"` (or missing from the response) has **no active mining** — it is paused or waiting for the next phase. Only markets with a non-zero value pay the bonus.

**Worked example**

A user supplies `1,000` USDD into jUSDD. With `supplyRate = 0.012` and `apy = 0.09175706`:

- Base supply yield: `1000 × 0.012 = 12 USDD / year`
- Mining bonus:     `1000 × 0.09175706 = 91.76 USDD / year`
- **Combined:**     `~103.76 USDD / year (≈ 10.38 % total APY)`

---

### 4.2 `GET /mining/reward` — Current phase status for a user

Returns the active and previous mining phase for the given user, per market.

**Parameters**

| Name      | In    | Type   | Required | Description                                          |
|-----------|-------|--------|----------|------------------------------------------------------|
| `address` | query | string | yes      | Single TRON wallet address.                          |

**Example request**

```http
GET /mining/reward?address=T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb
```

**Response data** (real response captured 2026-07-15 — note the payload is keyed by **market address**, then by **reward-token symbol**, currently `USDD`)

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "TKFRELGGoRgiayhwJTNNLqCNjFoLBh3Mnf": {
      "USDD": {
        "currPhase":         "120",
        "currStartTime":     "2026-07-11 20:00",
        "currEndTime":       "2026-07-18 20:00",
        "currReward":        "0.000000000000000000",
        "currRewardStatus":  "1",
        "lastStartTime":     "2026-07-04 20:00",
        "lastEndTime":       "2026-07-11 20:00",
        "lastReward":        "0",
        "lastRewardStatus":  "2",
        "price":             "1.000000000000000000"
      }
    }
  }
}
```

**Field reference**

| Field              | Type    | Required | Unit              | Description                                                                       |
|--------------------|---------|----------|-------------------|-----------------------------------------------------------------------------------|
| key (top‑level)    | string  | —        | jToken address    | Market the rewards refer to (`TKFREL…` = `jUSDD`).                                |
| key (2nd level)    | string  | —        | reward token      | Reward-token symbol (currently `USDD`). The reward object sits under this key.    |
| `currPhase`        | string  | Yes      | count             | Sequential phase number that is **in progress** now. Integer serialized as string.|
| `currStartTime`    | string  | Yes      | `YYYY-MM-DD HH:mm`| Start of current phase (no timezone designator returned).                         |
| `currEndTime`      | string  | Yes      | `YYYY-MM-DD HH:mm`| End of current phase.                                                             |
| `currReward`       | string  | Yes      | USDD              | Estimated/accrued reward for the user in the current phase. Decimal string.       |
| `currRewardStatus` | string  | Yes      | enum string       | `"0"`=not started, `"1"`=ongoing, `"2"`=ended (claimable), `"3"`=paused.          |
| `lastStartTime`    | string  | Yes      | `YYYY-MM-DD HH:mm`| Start of previous (most recently finalized) phase.                                |
| `lastEndTime`      | string  | Yes      | `YYYY-MM-DD HH:mm`| End of previous phase.                                                            |
| `lastReward`       | string  | Yes      | USDD              | Finalized reward for the user in the previous phase. Use `/mining/distributions` to fetch the claim proof. Decimal string. |
| `lastRewardStatus` | string  | Yes      | enum string       | Same enum as `currRewardStatus`. Usually `"2"` (ended/claimable).                 |
| `price`            | string  | Yes      | USD               | Current price of the **reward token** (USDD ≈ 1 USD). Decimal string.             |

---

### 4.3 `GET /mining/distributions` — Claim proofs for all phases

Returns **every** mining phase the user has ever been entitled to, including claimed and unclaimed phases. Each entry carries the Merkle proof needed to call the on‑chain claim function.

**Parameters**

| Name   | In    | Type   | Required | Description                                          |
|--------|-------|--------|----------|------------------------------------------------------|
| `addr` | query | string | yes      | Single TRON wallet address. ⚠️ **The parameter is named `addr` on this endpoint** (unlike `/mining/reward`, which uses `address`). Sending `address` returns `{"code":1,"message":"Required request parameter 'addr' ... is not present"}`. |

**Example request**

```http
GET /mining/distributions?addr=TB2e78zyzMnaNG2GRazazmbVVv3J564YHg
```

**Response data** (real response captured 2026-07-15, truncated to 1 of 10 phases and 2 proof elements — note the keys are **bare phase numbers**, e.g. `"22"`)

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "22": {
      "tokenAddress": "TPYmHEhy5n8TCEfYGqW2rPxsghSfzghPDn",
      "tokenSymbol":  "USDDOLD",
      "claimed":      false,
      "merkleIndex":  "0x00",
      "index":        "0x04b6",
      "amount":       "0x40086576c6adc75c",
      "merkleRoot":   "0x3fdc21ab4fed9e13714fa852ff2e659f9e32af553f4426810ff75e38ccf17a97",
      "proof": [
        "0x00ffb450e721c910fc2b305b1184ddc9e8fe6c014cb514ac6753c2bddd3e68c2",
        "0x7e31527db07b9a464e5467853ef325426d3d4cae8b180638cb8dfb32e60e7ff5"
      ],
      "prices":       "1"
    }
  }
}
```

**Field reference**

| Field          | Type           | Required | Format                 | Description                                                                                       |
|----------------|----------------|----------|------------------------|---------------------------------------------------------------------------------------------------|
| key (`"N"`)    | string         | —        | phase number           | Phase number as a string, e.g. `"22"`. Phases are 1‑based and monotonically increasing. (Older docs showed the label `"Phase 22"`; the service returns the bare number.) |
| `tokenAddress` | string         | Yes      | TRON address           | Reward (distribution) token address for this phase.                                               |
| `tokenSymbol`  | string         | Yes      | text                   | Reward token symbol for this phase (e.g. `USDDOLD`).                                              |
| `claimed`      | boolean        | Yes      | true / false           | `true` if the user has already claimed this phase, `false` if still claimable.                    |
| `merkleIndex`  | string         | Yes      | hex `uint256`          | Index of the Merkle tree this phase belongs to (some contracts maintain multiple trees).          |
| `index`        | string         | Yes      | hex `uint256`          | Leaf index of the user inside the Merkle tree.                                                    |
| `amount`       | string         | Yes      | hex `uint256`          | Claimable reward amount in the **reward token's smallest units** — look up the token's `decimals` (USDD / USDDOLD have **18**; see [`contracts.json`](contracts.json)). |
| `merkleRoot`   | string         | Yes      | hex `bytes32`          | Merkle root of this phase.                                                                        |
| `proof`        | array&lt;string&gt; | Yes | hex `bytes32` each     | Merkle proof from the user's leaf to `merkleRoot`.                                                |
| `prices`       | string         | Yes      | USD (decimal string)   | Price of the reward token in USD.                                                                 |

> **All hex strings are bare `0x…` values.** Older docs may show a leading `:` (e.g. `:0x6933158b3c05`); that colon is a delimiter and is **not** part of the value.

#### Decoding `amount`

`amount` is in the reward token's smallest units. Fetch the token's `decimals` (from [`contracts.json`](contracts.json) or the TRC20 contract) — USDD and USDDOLD both have **18**:

```python
# Python
hex_amount = "0x40086576c6adc75c"
raw        = int(hex_amount, 16)              # 4614192507070891868
human_usdd = raw / 10 ** 18                   # 4.614192507070892 (USDDOLD has 18 decimals)
```

```js
// JS / TS — use BigInt for safety
const raw       = BigInt("0x40086576c6adc75c");
const humanUsdd = Number(raw) / 1e18;         // token decimals = 18 for USDD / USDDOLD
```

#### Typical claim workflow

1. `GET /mining/distributions?addr={user}`
2. Filter entries where `claimed == false`.
3. For each unclaimed phase, call the distribution contract's `claim` function with `(merkleIndex, index, amount, proof)` (the contract verifies them against the stored `merkleRoot`).
4. After the on‑chain transaction succeeds, the next API call returns `claimed: true`.

---

## 5. Staked TRX & Energy Rental

### 5.1 `GET /lend/strx` — sTRX market & Energy Rental snapshot

Returns global state for the sTRX liquid‑staking pool and the Energy Rental market.

**Parameters:** none.

**Response data** (real response captured 2026-07-15)

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "stakeInfo": {
      "strxAddress":         "TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5",
      "symbol":              "sTRX",
      "decimal":             "18",
      "totalSupply":         "7416931940.940514882265682812",
      "totalSupplyUsd":      "3173929709.88356922",
      "exchangeRate":        "1.306200515551643308",
      "totalUnderlying":     "9688000325.067951",
      "underlyingDecimal":   "6",
      "rentReserveFactor":   "0.200000000000000000",
      "rewardReserveFactor": "0.200000000000000000",
      "reserves":            "290201700.064348",
      "supplyRate":          "0.03162947",
      "trxPrice":            "0.327614533793000000"
    },
    "rentInfo": {
      "rentMarketAddress":       "TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd",
      "priceFor10KEnergByRent":  "0.44835366",
      "priceFor10KEnergByStake": "1053.43779485",
      "priceFor10KEnergByBurn":  "1.00000000",
      "totalDelegatedEnergyTrx": "506918969.020237",
      "totalDelegatedEnergyRate":"0.10138379"
    }
  }
}
```

**`stakeInfo` field reference**

| Field                 | Type    | Required | Unit                   | Description                                                                          |
|-----------------------|---------|----------|------------------------|--------------------------------------------------------------------------------------|
| `strxAddress`         | string  | Yes      | TRON address           | sTRX token contract.                                                                 |
| `symbol`              | string  | Yes      | text                   | Token symbol (`sTRX`).                                                               |
| `decimal`             | string  | Yes      | count                  | sTRX decimals (`"18"`). ⚠️ Integer serialized as a **string** on this endpoint.      |
| `underlyingDecimal`   | string  | Yes      | count                  | TRX decimals (`"6"`). ⚠️ Integer serialized as a **string** on this endpoint.        |
| `exchangeRate`        | string  | Yes      | TRX per sTRX           | Current redemption rate. `"1.30"` means 1 sTRX = 1.30 TRX. Decimal string.           |
| `supplyRate`          | string  | Yes      | annualized decimal     | sTRX staking APY. `"0.0316"` = `3.16 % APY`. Decimal string.                         |
| `totalSupply`         | string  | Yes      | sTRX units             | Total sTRX issued. Decimal string.                                                   |
| `totalUnderlying`     | string  | Yes      | TRX                    | Total TRX held by the pool. Decimal string.                                          |
| `totalSupplyUsd`      | string  | Yes      | USD                    | TVL of the sTRX pool in USD. Decimal string.                                         |
| `trxPrice`            | string  | Yes      | USD                    | Current TRX price. Decimal string.                                                   |
| `reserves`            | string  | Yes      | TRX                    | Protocol reserves. Decimal string. (Historical responses used the misspelled key `reserse`; the service now returns `reserves` — tolerate both when reading old captures.) |
| `rentReserveFactor`   | string  | Yes      | decimal (0–1)          | Share of rental revenue taken as reserve. Decimal string.                            |
| `rewardReserveFactor` | string  | Yes      | decimal (0–1)          | Share of staking reward taken as reserve. Decimal string.                            |

**`rentInfo` field reference**

| Field                       | Type    | Required | Unit               | Description                                                                                          |
|-----------------------------|---------|----------|--------------------|------------------------------------------------------------------------------------------------------|
| `rentMarketAddress`         | string  | Yes      | TRON address       | Energy Rental contract.                                                                              |
| `priceFor10KEnergByRent`    | string  | Yes      | TRX / 10 000 ⚡    | TRX cost to obtain 10 000 Energy via **rental** (cheapest path). Decimal string.                     |
| `priceFor10KEnergByStake`   | string  | Yes      | TRX / 10 000 ⚡    | TRX **stake** required to produce 10 000 Energy yourself. Decimal string.                            |
| `priceFor10KEnergByBurn`    | string  | Yes      | TRX / 10 000 ⚡    | TRX cost to obtain 10 000 Energy by **burning** TRX in a transaction. Decimal string.                |
| `totalDelegatedEnergyTrx`   | string  | Yes      | TRX                | Total TRX delegated through the rental market. Decimal string.                                       |
| `totalDelegatedEnergyRate`  | string  | Yes      | decimal (0–1)      | Utilization rate of the rental pool. Decimal string.                                                 |

---

### 5.2 `GET /lend/strxStake/account` — User sTRX positions

**Parameters**

| Name             | In    | Type    | Required | Description                                                  |
|------------------|-------|---------|----------|--------------------------------------------------------------|
| `addresses`      | query | string  | yes      | One or more TRON addresses, comma‑separated.                 |
| `pageNo`         | query | integer | no       | 1‑based page number. Default `1`.                            |
| `pageSize`       | query | integer | no       | Page size. Default `10`, max `1000`.                         |
| `minStrxBalance` | query | number  | no       | Only include accounts with sTRX balance ≥ this threshold.    |

**Response data** (real response captured 2026-07-15)

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "totalPage":  1,
    "totalCount": 1,
    "list": [
      {
        "address":                 "TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5",
        "availableWithdrawAmount": "804814121.102239",
        "unstakingAmount":         "53899847.795703",
        "sTRXBalance":             "1.000000000000000000"
      }
    ]
  }
}
```

| Field                     | Type   | Required | Unit | Description                                                                  |
|---------------------------|--------|----------|------|------------------------------------------------------------------------------|
| `address`                 | string | Yes      | —    | User wallet. (Earlier versions of this page showed the key as `addresses`; the service returns `address`.) |
| `sTRXBalance`             | string | Yes      | sTRX | Current sTRX balance. Decimal string.                                        |
| `unstakingAmount`         | string | Yes      | TRX  | Amount currently in the un‑staking cooldown period. Decimal string.          |
| `availableWithdrawAmount` | string | Yes      | TRX  | TRX already through the cooldown and ready to withdraw. Decimal string.      |

---

### 5.3 `GET /lend/rentResource/account` — User Energy Rental positions

Currently only **Energy** rentals are exposed.

**Parameters**

| Name                     | In    | Type    | Required | Description                                                       |
|--------------------------|-------|---------|----------|-------------------------------------------------------------------|
| `addresses`              | query | string  | yes      | One or more TRON addresses, comma‑separated.                      |
| `pageNo`                 | query | integer | no       | 1‑based page number. Default `1`.                                 |
| `pageSize`               | query | integer | no       | Page size. Default `10`, max `1000`.                              |
| `minStrxBalance`         | query | number  | no       | Filter by minimum sTRX balance held by the renter.                |
| `maxRemainingRentAmount` | query | number  | no       | Only include orders with remaining rent ≤ this threshold.         |

**Response data** (values illustrative; decimal amounts are returned as strings, like every other endpoint)

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "totalCount": 1,
    "totalPage":  1,
    "list": [
      {
        "rentType":         "Energy",
        "renter":           "TWdWEHRLPBVGsXhwjSUv45XwnsfUHXydJa",
        "receiver":         "TWdWEHRLPBVGsXhwjSUv45XwnsfUHXydJa",
        "delegatedAmount":  "10000.000000",
        "rentRemainAmount": "8500.000000",
        "rentAmountPerDay": "1500.000000"
      }
    ]
  }
}
```

| Field              | Type   | Required | Unit         | Description                                              |
|--------------------|--------|----------|--------------|----------------------------------------------------------|
| `rentType`         | string | Yes      | enum         | `"Energy"`. Bandwidth not exposed yet.                   |
| `renter`           | string | Yes      | TRON address | The account paying the rent.                             |
| `receiver`         | string | Yes      | TRON address | The account receiving the delegated Energy.              |
| `delegatedAmount`  | string | Yes      | TRX          | TRX equivalent of the energy currently delegated. Decimal string. |
| `rentRemainAmount` | string | Yes      | TRX          | TRX prepayment still remaining for this order. Decimal string. |
| `rentAmountPerDay` | string | Yes      | TRX / day    | Daily TRX cost of the rental order. Decimal string.      |

---

## 6. Quick reference for AI agents

If you are an LLM tool building requests against this API, follow these rules:

1. **All endpoints are `GET` against `https://openapi.just.network`.**
2. **All responses are wrapped in `{code, message, data}`. Check the success code before reading `data`: `code == 0` on V1 endpoints, `code == 200` on `/v2/...` endpoints** (see §1.1).
3. **Decimal quantities arrive as JSON strings and are already de‑scaled** — parse with big-decimal/BigInt, and never multiply by `1e18` / `1e6` again unless explicitly told (the exceptions: `amount` / `index` in `/mining/distributions` are hex `uint256` in raw smallest units; `borrowIndex` and the V2 `shareAmount` / `borrowShares` are raw integer strings).
4. **Rates (`*Rate`, `apy`) are annualized decimals.** Multiply by 100 for `%`.
5. **A market's effective supply APY** = `tokenList[i].supplyRate` + (mining apy if `tokenList[i].address` has a non-zero value in `/mining/apy`, else 0).
6. **Address‑keyed objects** — look up the jToken address in §2 to know which market a sub‑object refers to.
7. **Liquidations** — pull `/justlend/liquidate/highRiskAccountList` periodically; `risk > 1` ⇒ liquidatable.
8. **Mining claims** — every entry of `/mining/distributions` (parameter `addr`, not `address`) with `claimed == false` is a free transaction the user should submit.
9. **V2 (Moolah)** — discover vaults via `/v2/index/vault/list` and markets via `/v2/index/market/list`, then read one user's positions via `/v2/index/position`, `/v2/vault/position` (by `vaultAddress`) and `/v2/market/position` (by `market` id). See §3.4.

The machine‑readable OpenAPI 3.1 spec lives at [`apis/justlend_apis.yaml`](./apis/justlend_apis.yaml). It is maintained together with this page and verified against the live service (last verified 2026-07-15 — see the [agent acceptance run](apis/agent-acceptance.md)); **if the two ever diverge, treat the YAML as authoritative** ([§1.8](#18-versioning-and-compatibility)) and please report the mismatch.

---

## 7. Interactive API Explorer

Use the embedded Swagger UI below to call endpoints directly from this page. Same OpenAPI spec as the YAML link above.

<swagger-ui src="../developers/apis/justlend_apis.yaml" />

---

## 8. Event-stream and indexing options

The HTTP API exposes **current state**. For **historical events** (every `Mint`, `Borrow`, `RepayBorrow`, `Redeem`, `LiquidateBorrow`, `enterMarkets`, governance `ProposalCreated`/`VoteCast`/`ProposalExecuted`, sTRX `Deposit`/`Withdrawal`, EnergyRental `RentResource`/`ReturnResource`) you need an event source.

**There is currently no official JustLend subgraph or hosted indexer.** Use one of these patterns instead:

### 8.1 TronGrid event filter (recommended for low-volume queries)

[TronGrid](https://www.trongrid.io/) exposes `GET /v1/contracts/{address}/events` for any contract. Filter by `event_name` and time range. Free tier covers most ad-hoc analytics; paid tiers raise the rate limit.

```bash
# All Mint events on jUSDT for the last hour
curl -H "TRON-PRO-API-KEY: $TRONGRID_API_KEY" \
  "https://api.trongrid.io/v1/contracts/TXJgMdjVX5dKiQaUi9QobwNxtSQaFqccvd/events?event_name=Mint&min_block_timestamp=$(($(date +%s%3N)-3600000))"
```

Pros: zero setup, well-documented, works for any JustLend contract. Cons: cursored pagination only, ~30-day retention on the free tier, not great for full historical backfills.

### 8.2 Self-hosted indexer (recommended for production analytics)

Stand up an indexer that consumes block ranges and writes typed event tables. TRON's EVM compatibility is partial (different signature scheme, different fee model, different address encoding) so most "EVM-indexer" tooling needs a TRON-specific datasource — verify support before adopting.

- **Custom decoder against a TRON archive endpoint (most robust path).** Run `java-tron` in archive mode, or use a TronGrid full-archive plan, and decode events with the JSON ABIs at [`/developers/abis/`](abis/jtoken.json). Write your own schema; commit indices on `(market, block_number)` for the per-market views you need. Most operational overhead, most flexibility, no third-party dependency.
- **Generic EVM indexers (DipDup, Subsquid, Substreams, Goldsky, etc.).** These have evolving TRON support — some via official adapters, some via community forks, some not at all. Treat any "DipDup/Subsquid supports TRON" claim as needing verification against the project's current docs and your specific event-decoding needs. None of these are recommended without a proof-of-concept run against a TRON archive endpoint first.
- **Tron-native option: TronGrid event API.** §8.1 covers this; for low-to-mid volume it removes the need for a self-hosted indexer entirely.

### 8.3 MCP server `read_events` (when integrating with an AI agent)

For low-volume agent-driven queries, the [full MCP server](../ai_support/mcp_server.md) exposes contract read primitives that can be composed into event lookups (`get_account_summary`, `get_market_data`, etc.). For raw event log access, fall back to TronGrid via your own tooling — MCP is not optimized for historical-event sweeps.

### 8.4 Quick reference: event signatures by contract

ABIs at [`/developers/abis/`](abis/jtoken.json) carry the canonical event signatures. The most commonly indexed:

| Contract | Event | Topic 0 (keccak256 signature hash) |
|---|---|---|
| jToken (`jtoken.json`) | `Mint(address minter, uint mintAmount, uint mintTokens)` | derived from ABI |
| jToken | `Borrow(address borrower, uint borrowAmount, uint accountBorrows, uint totalBorrows)` | derived from ABI |
| jToken | `RepayBorrow(address payer, address borrower, uint repayAmount, uint accountBorrows, uint totalBorrows)` | derived from ABI |
| jToken | `Redeem(address redeemer, uint redeemAmount, uint redeemTokens)` | derived from ABI |
| jToken | `LiquidateBorrow(address liquidator, address borrower, uint repayAmount, address cTokenCollateral, uint seizeTokens)` | derived from ABI |
| Comptroller (`comptroller.json`) | `MarketEntered(CToken cToken, address account)` | derived from ABI |
| Comptroller | `MarketExited(CToken cToken, address account)` | derived from ABI |
| GovernorBravo (`governor-alpha.json`) | `ProposalCreated`, `VoteCast`, `ProposalExecuted`, `ProposalCanceled` | derived from ABI |
| sTRX (`strx.json`) | `Deposit(address user, uint trxAmount, uint sTRXAmount)`, `WithdrawRequested`, `Claim` | derived from ABI |
| EnergyRental (`energy-market.json`) | `RentResource(address renter, address receiver, uint amount, uint resourceType)`, `ReturnResource`, `Liquidate` | derived from ABI |

Compute the topic 0 with any standard tool: `web3.utils.sha3('Mint(address,uint256,uint256)')`. Avoid hard-coding topic hashes in source — derive from the JSON ABIs at runtime, since event signatures could change in a future upgrade.
