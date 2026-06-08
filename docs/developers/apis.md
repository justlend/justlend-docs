---
title: JustLend DAO API Reference
description: Public read-only REST API at openapi.just.network — markets, account positions, liquidation risk, USDD supply-mining rewards, sTRX staking, Energy Rental. Authoritative schema is the OpenAPI 3.1 YAML.
---

# JustLend DAO API

Public REST endpoints for querying JustLend DAO protocol state: lending markets, user positions, liquidation risk, USDD supply‑mining rewards, sTRX staking, and Energy Rental.

## Contents

This page is the human-readable reference. The [OpenAPI 3.1 YAML](apis/justlend_apis.yaml) is the machine-readable contract — treat the YAML as authoritative if they ever diverge.

- [Quick start](#quick-start) — connectivity check + minimal response example.
- [§1 Conventions](#1-conventions) — response envelope, address format, numeric formats, rate / APY semantics, pagination, error responses, rate limits, versioning.
- [§2 jToken Address Reference](#2-jtoken-address-reference) — the 23-market table with `status: active|legacy` and the programmatic-filter tip.
- [§3 Supply & Borrow Market endpoints](#3-supply-borrow-market) — `/lend/jtoken`, `/lend/account`, `/justlend/liquidate/highRiskAccountList`.
- [§4 USDD Supply Mining](#4-usdd-supply-mining) — `/mining/reward`, `/mining/apy`, `/mining/distributions`.
- [§5 Staked TRX & Energy Rental](#5-staked-trx-energy-rental) — `/lend/strx`, `/lend/strxStake/account`, `/lend/rentResource/account`.
- [§6 Quick reference for AI agents](#6-quick-reference-for-ai-agents) — common end-to-end recipes.
- [§7 Interactive API Explorer](#7-interactive-api-explorer) — embedded Swagger UI.
- [§8 Event-stream and indexing options](#8-event-stream-and-indexing-options) — how to query historical Mint / Borrow / Repay events on TRON.

For gotchas while using these endpoints (USDT-style approve race, decimals mismatch, close-factor cap, etc.), see [Common Pitfalls](common_pitfalls.md). For precise term definitions, see the [Glossary](../resources/glossary.md).

- **Base URL:** `https://openapi.just.network`
- **Method:** All endpoints are `GET`. No authentication.
- **Content‑Type:** `application/json`
- **Machine‑readable spec:** [`justlend_apis.yaml`](./apis/justlend_apis.yaml) (OpenAPI 3.1). Importable into Swagger UI, Postman, Insomnia, or any LLM tool.
- **Rate limits:** The public service is unauthenticated and may throttle abusive traffic. Keep `pageSize <= 1000`, cache stable metadata such as jToken lists, and retry `429` / `5xx` responses with exponential backoff.

## Quick start

Run this read-only request to verify connectivity and inspect the current JustLend market list:

```bash
curl -sS https://openapi.just.network/lend/jtoken
```

Expected result (one token shown in full; real response has ~23 entries with the same shape):

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "tokenList": [
      {
        "address":              "TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP",
        "symbol":               "jTRX",
        "underlyingAddress":    "T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb",
        "underlyingSymbol":     "TRX",
        "underlyingDecimal":    6,
        "underlyingPriceInTrx": 1.0,
        "underlyingPriceInUsd": 0.21,
        "borrowIndex":          1224530412174750380,
        "borrowRate":           0.064673716541040000,
        "supplyRate":           0.009044500002192000,
        "apy":                  0.000000000000000000,
        "cash":                 349909392.537020000000000000,
        "totalSupply":          12345678901234,
        "totalBorrows":         123456789.012345,
        "reserveFactor":        0.20,
        "collateralFactor":     0.75,
        "exchangeRate":         200345678901234567890000000
      }
      /* ... 22 more entries ... */
    ]
  }
}
```

**Units cheat-sheet for the response above** (see [§1.3](#13-numeric-formats) and [§1.4](#14-rate-apy-semantics) for the full table):

- `borrowRate`, `supplyRate`, `apy`, `collateralFactor`, `reserveFactor` — annualized / fractional **decimals**. Multiply by 100 for percent. See [§1.4 Rate / APY semantics](#14-rate-apy-semantics) for the full table.
- `cash`, `totalBorrows` — already de-scaled by the underlying's decimals. Use as-is.
- `totalSupply` — **jToken** units (always 8 decimals).
- `borrowIndex`, `exchangeRate` — mantissa-scaled by `1e18` (see [Glossary → mantissa](../resources/glossary.md#mantissa)).

For integrations, import the OpenAPI schema from [`apis/justlend_apis.yaml`](./apis/justlend_apis.yaml), then start with `GET /lend/jtoken` for market metadata and `GET /lend/account?addresses={wallet}` for a user's positions.

---

## 1. Conventions

These conventions apply to **every** response unless an endpoint says otherwise.

### 1.1 Response envelope

Every successful response uses the same envelope:

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": { ... }
}
```

| Field     | Type    | Meaning                                                          |
|-----------|---------|------------------------------------------------------------------|
| `code`    | integer | `0` means success. Non‑zero values indicate an error.            |
| `message` | string  | `"SUCCESS"` on success, otherwise a short error description.     |
| `data`    | object  | Endpoint payload. Shape is documented per endpoint below.        |

### 1.2 Address format

All addresses are TRON **Base58** addresses (start with `T`, 34 chars). Examples: `TKFRELGGoRgiayhwJTNNLqCNjFoLBh3Mnf`.

### 1.3 Numeric formats

| Format                | Where it appears                                                                              | How to read it                                                                                        |
|-----------------------|-----------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| Decimal string/number | `borrowRate`, `supplyRate`, `apy`, `collateralFactor`, `health`, `risk`, `exchangeRate`, etc. | Already human‑readable. `0.064673` means `6.4673 %` for rates, `0.75` means `75 %` for factors.       |
| Underlying amount     | `cash`, `totalBorrows`, `reserves`, `supplyBalanceUnderlying`, `borrowBalanceUnderlying`      | Already de‑scaled by the asset's decimals. Use as‑is for display.                                     |
| jToken amount         | `totalSupply` of `/lend/jtoken`, `supplyBalanceJtoken`                                        | jToken units (jTokens always have **8** decimals on TRON).                                            |
| TRX value             | Anything ending in `InTrx`                                                                    | Already de‑scaled (TRX has 6 decimals). For example `totalBorrowValueInTrx: 11.277370` means 11.277 TRX. |
| USD value             | Anything ending in `Usd`                                                                      | Already de‑scaled US dollars.                                                                         |
| Hex string            | `amount`, `index`, `merkleIndex`, `merkleRoot`, `proof` in `/mining/distributions`            | Hex‑encoded `uint256`. **The leading `:` shown in some legacy examples is a delimiter and is not part of the value.** Pass directly to the on‑chain claim contract. |

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

**Business / validation errors — HTTP `200`, `code` ≠ 0, `data` omitted:**

```json
{ "code": 404, "message": "interface [/lend/nonExistentXYZ] non exist" }
```

| Signal | How to detect failure |
|--------|------------------------|
| Body `code` | `0` = success. Any non-zero value (e.g. `1`, `404`) is an error — read `message`; `data` is typically absent or `null`. |
| HTTP status | `200` for virtually all business/validation outcomes, **including "not found" and invalid parameters**. Do **not** use the HTTP status to detect business errors. |

**Transport-level statuses (the only non-`200` HTTP codes to expect):**

| HTTP status | Meaning | Retry |
|-------------|---------|-------|
| `429` | Too Many Requests — throttled. | Yes — exponential backoff (see §1.7). |
| `5xx` | Server error. | Yes — with backoff. |

**Silent parameter handling (must-know):** unknown or out-of-range query parameters (e.g. `pageSize=invalid`, `pageNo=-1`) are commonly **silently ignored** — the service returns `200 SUCCESS` with default data rather than rejecting the request. Some endpoints do return a non-zero `code` (e.g. `{"code":1,"message":"illegal pageNo or pageSize"}`), but **this is not guaranteed**. The API does **not** reliably validate inputs for you: **validate parameters client-side** and never assume a malformed request will fail.

> This error contract reflects the live service as of 2026-06-08. A future API revision may adopt HTTP status codes and/or a structured error body; until then, treat HTTP `200` + body `code` as authoritative and validate inputs client-side.

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
- Legacy fields can remain documented for compatibility. For example, `reserse` is preserved as returned by the service and should be read as `reserves`.
- When the rendered page and OpenAPI YAML differ, treat [`apis/justlend_apis.yaml`](./apis/justlend_apis.yaml) as the source of truth for request and response shapes.

---

## 2. jToken Address Reference

Several endpoints key their payloads by jToken address (e.g. `data["TKFRELGGoRgiayhwJTNNLqCNjFoLBh3Mnf"]`). Use this table to translate.

The protocol currently exposes **17 active + 6 legacy = 23 markets**. Legacy markets are closed to new supply and borrow — existing positions remain queryable so they can be unwound, but do not direct new deposits to them.

!!! tip "Programmatic filter"
    For agents that prefer not to parse prose: each entry in [`/developers/contracts.json` → `networks.mainnet.jtokens.<symbol>`](contracts.json) carries an explicit `status` field with value `"active"` or `"legacy"`. Filter `status == "active"` to get the 17 active markets, `status == "legacy"` to get the 6 legacy ones. The schema and enum are documented in [`contracts.schema.json`](contracts.schema.json).

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

**Response data**

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "tokenList": [
      {
        "address":              "TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP",
        "symbol":               "jTRX",
        "underlyingAddress":    "T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb",
        "underlyingSymbol":     "TRX",
        "underlyingDecimal":    6,
        "underlyingPriceInTrx": 1.0,
        "borrowIndex":          1224530412174750380,
        "borrowRate":           0.064673716541040000,
        "supplyRate":           0.009044500002192000,
        "cash":                 349909392.537020000000000000,
        "reserves":             2300647.881336000000000000,
        "totalBorrows":         63951044.565948000000000000,
        "totalSupply":          39391010299.49149122,
        "exchangeRate":         0.010448063811832339,
        "collateralFactor":     0.750000000000000000,
        "reserveFactor":        0.100000000000000000
      }
    ]
  }
}
```

**Field reference**

| Field                  | Type    | Unit / Format            | Description                                                                 |
|------------------------|---------|--------------------------|-----------------------------------------------------------------------------|
| `address`              | string  | TRON address             | jToken contract address (the market).                                       |
| `symbol`               | string  | text                     | jToken symbol, e.g. `jTRX`, `jUSDD`.                                        |
| `underlyingAddress`    | string  | TRON address             | Underlying asset contract address.                                          |
| `underlyingSymbol`     | string  | text                     | Underlying asset symbol.                                                    |
| `underlyingDecimal`    | integer | count                    | Decimals of the underlying asset.                                           |
| `underlyingPriceInTrx` | number  | TRX                      | Oracle price of 1 unit of underlying, denominated in TRX.                   |
| `borrowIndex`          | integer | scaled 1e18              | Cumulative borrow interest index. Used for accurate per‑user accounting.    |
| `borrowRate`           | number  | annualized decimal       | Borrow APY. `0.0647` = `6.47 %`.                                            |
| `supplyRate`           | number  | annualized decimal       | Supply APY (excluding mining).                                              |
| `cash`                 | number  | underlying units         | Available underlying liquidity in the market.                               |
| `reserves`             | number  | underlying units         | Protocol reserves in the market.                                            |
| `totalBorrows`         | number  | underlying units         | Total outstanding debt.                                                     |
| `totalSupply`          | number  | jToken units (8 decimals)| Total minted jTokens.                                                       |
| `exchangeRate`         | number  | underlying per jToken    | Current jToken → underlying conversion ratio.                               |
| `collateralFactor`     | number  | decimal (0–1)            | LTV cap when used as collateral. `0.75` = `75 %`.                           |
| `reserveFactor`        | number  | decimal (0–1)            | Share of borrow interest taken as protocol reserve.                         |

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

**Response data**

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "totalCount": 1,
    "totalPage": 1,
    "list": [
      {
        "addresses":                 "T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb",
        "health":                    5.88,
        "totalCollateralValueInTrx": 24.126681,
        "totalBorrowValueInTrx":     11.277370,
        "liquidateStatusStartTime":  null,
        "tokens": [
          {
            "address":                "TNSBA6KvSvMoTqQcEgpVK7VhHT3z7wifxy",
            "underlyingSymbol":       "USDD",
            "entered":                1,
            "supplyBalanceJtoken":    1.09062037,
            "supplyBalanceUnderlying":0.01148891329334797277745383,
            "borrowBalanceUnderlying":0.704372293431165977793198
          }
        ]
      }
    ]
  }
}
```

**Field reference**

| Field                       | Type    | Unit              | Description                                                                          |
|-----------------------------|---------|-------------------|--------------------------------------------------------------------------------------|
| `addresses`                 | string  | TRON address      | Wallet address.                                                                      |
| `health`                    | number  | ratio             | Health factor. `> 1` healthy, `≤ 1` liquidatable. `5.88` = very safe.                |
| `totalCollateralValueInTrx` | number  | TRX               | Sum of collateral value (after `collateralFactor`).                                   |
| `totalBorrowValueInTrx`     | number  | TRX               | Sum of outstanding borrow value.                                                     |
| `liquidateStatusStartTime`  | string\|null | ISO 8601    | Timestamp when this account first entered a liquidatable state, or `null` if safe.   |
| `tokens[].address`          | string  | TRON address      | jToken address of this position.                                                     |
| `tokens[].underlyingSymbol` | string  | text              | Underlying symbol, e.g. `USDD`.                                                      |
| `tokens[].entered`          | integer | 0 / 1             | `1` if the user has entered this market as collateral, `0` otherwise.                |
| `tokens[].supplyBalanceJtoken`     | number | jToken units (8d)| Supplied balance in jTokens.                                                         |
| `tokens[].supplyBalanceUnderlying` | number | underlying       | Supplied balance in underlying.                                                      |
| `tokens[].borrowBalanceUnderlying` | number | underlying       | Outstanding borrow in underlying.                                                    |

---

### 3.3 `GET /justlend/liquidate/highRiskAccountList` — High‑risk accounts

Returns accounts that are currently liquidatable or close to it. Use this to drive liquidation bots.

**Parameters:** none.

**Response data**

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "updateTime": 1770275708508,
    "jtokens": [ { "jUSDD": "TKFRELGGoRgiayhwJTNNLqCNjFoLBh3Mnf", "jTRX": "TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP", "...": "..." } ],
    "accounts": [
      {
        "borrower":                "TLc34aTvy1vBFzLvM9oz36ihhb7sVpQmgQ",
        "risk":                    "1.105684",
        "totalCollateralUsd":      "234.063780",
        "totalBorrowUsd":          "193.705172",
        "liquidateStatusStartTime":1770089973150,
        "collateralTokenList": [
          {
            "jtokenAddress":    "TR7BUFRQeq1w5jAZf1FKx85SHuX6PfMqsV",
            "symbol":           "jETH",
            "amount":           "11.03049909",
            "price":            "21.090028146702653201",
            "valueUsd":         "232.633536",
            "exchangeRate":     "0.010021847796289808",
            "collateralFactor": "0.750000000000000000"
          }
        ],
        "borrowTokenList": [
          {
            "tokenAddress":     "TCFLL5dx5ZJdKnWuesXxi1VPwjLVmWZZy9",
            "symbol":           "JST",
            "amount":           "19.357667866419444238",
            "price":            "0.040802750477000000",
            "valueUsd":         "0.789846",
            "exchangeRate":     "0.010481635809265784",
            "collateralFactor": "0.600000000000000000"
          }
        ]
      }
    ]
  }
}
```

**Field reference**

| Field                                 | Type    | Unit                | Description                                                                                |
|---------------------------------------|---------|---------------------|--------------------------------------------------------------------------------------------|
| `updateTime`                          | integer | epoch ms            | When the snapshot was computed.                                                            |
| `jtokens`                             | object  | symbol → address    | jToken symbol‑to‑address lookup. Same data as §2.                                          |
| `accounts[].borrower`                 | string  | TRON address        | Borrower wallet.                                                                           |
| `accounts[].risk`                     | string  | ratio               | **Higher = riskier.** `> 1` means the account is liquidatable now.                          |
| `accounts[].totalCollateralUsd`       | string  | USD                 | Total collateral value.                                                                    |
| `accounts[].totalBorrowUsd`           | string  | USD                 | Total borrow value.                                                                        |
| `accounts[].liquidateStatusStartTime` | integer | epoch ms            | When the account first became liquidatable.                                                |
| `accounts[].collateralTokenList[]`    | array   | object              | One entry per collateral position (see below).                                             |
| `accounts[].borrowTokenList[]`        | array   | object              | One entry per borrow position (see below).                                                 |
| `collateralTokenList[].jtokenAddress` | string  | TRON address        | jToken address of the collateral.                                                          |
| `collateralTokenList[].amount`        | string  | jToken units (8d)   | Amount of jTokens held as collateral.                                                      |
| `collateralTokenList[].price`         | string  | USD                 | Current price of the **jToken** in USD (already multiplied by `exchangeRate`).             |
| `collateralTokenList[].valueUsd`      | string  | USD                 | `amount × price`.                                                                          |
| `collateralTokenList[].exchangeRate`  | string  | underlying / jToken | jToken → underlying conversion ratio.                                                      |
| `collateralTokenList[].collateralFactor` | string | decimal (0–1)    | Collateral factor applied for risk calculation.                                            |
| `borrowTokenList[].tokenAddress`      | string  | TRON address        | **Underlying** asset address (note: this list keys by underlying, not jToken).             |
| `borrowTokenList[].amount`            | string  | underlying          | Outstanding borrowed amount of underlying.                                                 |
| `borrowTokenList[].price`             | string  | USD                 | Underlying asset price.                                                                    |
| `borrowTokenList[].valueUsd`          | string  | USD                 | `amount × price`.                                                                          |

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

**Response data**

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "TKFRELGGoRgiayhwJTNNLqCNjFoLBh3Mnf": {
      "USDD": 0.09175706
    }
  }
}
```

**Field reference**

| Field            | Type    | Unit                | Description                                                                                       |
|------------------|---------|---------------------|---------------------------------------------------------------------------------------------------|
| key (top‑level)  | string  | jToken address      | The market the reward applies to. Look up in §2 (here `TKFREL…` is `jUSDD`).                       |
| `USDD`           | number  | annualized decimal  | USDD mining APY paid to suppliers of this market. `0.09175706` = **9.18 % APY**, on top of `supplyRate`. |

> If a market is missing from the response, mining is **not active** there. If `USDD` is `0`, mining is paused / waiting for the next phase.

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

**Response data**

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "TKFRELGGoRgiayhwJTNNLqCNjFoLBh3Mnf": {
      "currPhase":         64,
      "currStartTime":     "2026-05-12T00:00:00Z",
      "currEndTime":       "2026-05-19T00:00:00Z",
      "currReward":        0.0000,
      "currRewardStatus":  1,
      "lastStartTime":     "2026-05-05T00:00:00Z",
      "lastEndTime":       "2026-05-12T00:00:00Z",
      "lastReward":        0.0000,
      "lastRewardStatus":  2,
      "price":             1.000000000000000000
    }
  }
}
```

**Field reference**

| Field              | Type    | Unit              | Description                                                                       |
|--------------------|---------|-------------------|-----------------------------------------------------------------------------------|
| key (top‑level)    | string  | jToken address    | Market the rewards refer to (`TKFREL…` = `jUSDD`).                                |
| `currPhase`        | integer | count             | Sequential phase number that is **in progress** now.                              |
| `currStartTime`    | string  | ISO 8601 UTC      | Start of current phase.                                                           |
| `currEndTime`      | string  | ISO 8601 UTC      | End of current phase.                                                             |
| `currReward`       | number  | USDD              | Estimated/accrued reward for the user in the current phase. Updates over time.    |
| `currRewardStatus` | integer | enum              | `0`=not started, `1`=ongoing, `2`=ended (claimable), `3`=paused.                  |
| `lastStartTime`    | string  | ISO 8601 UTC      | Start of previous (most recently finalized) phase.                                |
| `lastEndTime`      | string  | ISO 8601 UTC      | End of previous phase.                                                            |
| `lastReward`       | number  | USDD              | Finalized reward for the user in the previous phase. Use `/mining/distributions` to fetch the claim proof. |
| `lastRewardStatus` | integer | enum              | Same enum as `currRewardStatus`. Usually `2` (ended/claimable).                   |
| `price`            | number  | USD               | Current price of the **reward token** (USDD ≈ 1 USD).                             |

---

### 4.3 `GET /mining/distributions` — Claim proofs for all phases

Returns **every** mining phase the user has ever been entitled to, including claimed and unclaimed phases. Each entry carries the Merkle proof needed to call the on‑chain claim function.

**Parameters**

| Name      | In    | Type   | Required | Description                                          |
|-----------|-------|--------|----------|------------------------------------------------------|
| `address` | query | string | yes      | Single TRON wallet address.                          |

**Example request**

```http
GET /mining/distributions?address=T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb
```

**Response data**

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "Phase 22": {
      "tokenAddress": "TPYmHEhy5n8TCEfYGqW2rPxsghSfzghPDn",
      "claimed":      false,
      "merkleIndex":  "0x00",
      "index":        "0x0659",
      "amount":       "0x6933158b3c05",
      "merkleRoot":   "0x3fdc21ab4fed9e13714fa852ff2e659f9e32af553f4426810ff75e38ccf17a97",
      "proof": [
        "0x6b734d20b9ca2a0dda57b184789dbb6df2d2993049a9365b6eafe932cd435255",
        "0xb1c6c5a90e8c2b8e6b1aa9b2ffaef1f0a36c12c3f95dd84d96cd6f8a9b0a0a0a"
      ]
    }
  }
}
```

**Field reference**

| Field          | Type           | Format                 | Description                                                                                       |
|----------------|----------------|------------------------|---------------------------------------------------------------------------------------------------|
| key (`Phase N`)| string         | text                   | Phase label, e.g. `"Phase 22"`. Phases are 1‑based and monotonically increasing.                  |
| `tokenAddress` | string         | TRON address           | Distribution contract address for this phase.                                                     |
| `claimed`      | boolean        | true / false           | `true` if the user has already claimed this phase, `false` if still claimable.                    |
| `merkleIndex`  | string         | hex `uint256`          | Index of the Merkle tree this phase belongs to (some contracts maintain multiple trees).          |
| `index`        | string         | hex `uint256`          | Leaf index of the user inside the Merkle tree.                                                    |
| `amount`       | string         | hex `uint256`          | Claimable reward amount in **underlying smallest units** (USDD = 6 decimals).                     |
| `merkleRoot`   | string         | hex `bytes32`          | Merkle root of this phase.                                                                        |
| `proof`        | array&lt;string&gt; | hex `bytes32` each | Merkle proof from the user's leaf to `merkleRoot`.                                                |

> **All hex strings are bare `0x…` values.** Older docs may show a leading `:` (e.g. `:0x6933158b3c05`); that colon is a delimiter and is **not** part of the value.

#### Decoding `amount`

```python
# Python
hex_amount = "0x6933158b3c05"
raw        = int(hex_amount, 16)              # 115698932195333
human_usdd = raw / 10 ** 6                    # 115698932.195333
```

```js
// JS / TS — use BigInt for safety
const raw       = BigInt("0x6933158b3c05");
const humanUsdd = Number(raw) / 1e6;
```

#### Typical claim workflow

1. `GET /mining/distributions?address={user}`
2. Filter entries where `claimed == false`.
3. For each unclaimed phase, call the distribution contract's `claim` function with `(merkleIndex, index, amount, proof)` (the contract verifies them against the stored `merkleRoot`).
4. After the on‑chain transaction succeeds, the next API call returns `claimed: true`.

---

## 5. Staked TRX & Energy Rental

### 5.1 `GET /lend/strx` — sTRX market & Energy Rental snapshot

Returns global state for the sTRX liquid‑staking pool and the Energy Rental market.

**Parameters:** none.

**Response data**

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "stakeInfo": {
      "strxAddress":         "TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5",
      "symbol":              "sTRX",
      "decimal":             18,
      "underlyingDecimal":   6,
      "exchangeRate":        1.181813870419231022,
      "supplyRate":          0.03937302,
      "totalSupply":         6553955254.250487546804870562,
      "totalUnderlying":     7745555225.580224,
      "totalSupplyUsd":      1729932328.75828661,
      "trxPrice":            0.223345167438102719,
      "reserse":             71933070.321420,
      "rentReserveFactor":   0.200000000000000000,
      "rewardReserveFactor": 0.200000000000000000
    },
    "rentInfo": {
      "rentMarketAddress":       "TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd",
      "priceFor10KEnergByRent":  0.65530713,
      "priceFor10KEnergByStake": 885.28697646,
      "priceFor10KEnergByBurn":  4.20000000,
      "totalDelegatedEnergyTrx": 162748507.908930,
      "totalDelegatedEnergyRate":0.03254970
    }
  }
}
```

**`stakeInfo` field reference**

| Field                 | Type    | Unit                   | Description                                                                          |
|-----------------------|---------|------------------------|--------------------------------------------------------------------------------------|
| `strxAddress`         | string  | TRON address           | sTRX token contract.                                                                 |
| `symbol`              | string  | text                   | Token symbol (`sTRX`).                                                               |
| `decimal`             | integer | count                  | sTRX decimals (`18`).                                                                |
| `underlyingDecimal`   | integer | count                  | TRX decimals (`6`).                                                                  |
| `exchangeRate`        | number  | TRX per sTRX           | Current redemption rate. `1.18` means 1 sTRX = 1.18 TRX.                             |
| `supplyRate`          | number  | annualized decimal     | sTRX staking APY. `0.0394` = `3.94 % APY`.                                           |
| `totalSupply`         | number  | sTRX units             | Total sTRX issued.                                                                   |
| `totalUnderlying`     | number  | TRX                    | Total TRX held by the pool.                                                          |
| `totalSupplyUsd`      | number  | USD                    | TVL of the sTRX pool in USD.                                                         |
| `trxPrice`            | number  | USD                    | Current TRX price.                                                                   |
| `reserse`             | number  | TRX                    | Protocol reserves (**typo preserved for backwards compatibility** — read as `reserves`). |
| `rentReserveFactor`   | number  | decimal (0–1)          | Share of rental revenue taken as reserve.                                            |
| `rewardReserveFactor` | number  | decimal (0–1)          | Share of staking reward taken as reserve.                                            |

**`rentInfo` field reference**

| Field                       | Type    | Unit               | Description                                                                                          |
|-----------------------------|---------|--------------------|------------------------------------------------------------------------------------------------------|
| `rentMarketAddress`         | string  | TRON address       | Energy Rental contract.                                                                              |
| `priceFor10KEnergByRent`    | number  | TRX / 10 000 ⚡    | TRX cost to obtain 10 000 Energy via **rental** (cheapest path).                                     |
| `priceFor10KEnergByStake`   | number  | TRX / 10 000 ⚡    | TRX **stake** required to produce 10 000 Energy yourself.                                            |
| `priceFor10KEnergByBurn`    | number  | TRX / 10 000 ⚡    | TRX cost to obtain 10 000 Energy by **burning** TRX in a transaction.                                |
| `totalDelegatedEnergyTrx`   | number  | TRX                | Total TRX delegated through the rental market.                                                       |
| `totalDelegatedEnergyRate`  | number  | decimal (0–1)      | Utilization rate of the rental pool.                                                                 |

---

### 5.2 `GET /lend/strxStake/account` — User sTRX positions

**Parameters**

| Name             | In    | Type    | Required | Description                                                  |
|------------------|-------|---------|----------|--------------------------------------------------------------|
| `addresses`      | query | string  | yes      | One or more TRON addresses, comma‑separated.                 |
| `pageNo`         | query | integer | no       | 1‑based page number. Default `1`.                            |
| `pageSize`       | query | integer | no       | Page size. Default `10`, max `1000`.                         |
| `minStrxBalance` | query | number  | no       | Only include accounts with sTRX balance ≥ this threshold.    |

**Response data**

```json
{
  "code": 0,
  "message": "SUCCESS",
  "data": {
    "totalCount": 1,
    "totalPage":  1,
    "list": [
      {
        "addresses":             "TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5",
        "sTRXBalance":           1.000000000000000000,
        "availableWithdrawAmount":150865439.643028,
        "unstakingAmount":       24120999.583032
      }
    ]
  }
}
```

| Field                     | Type   | Unit | Description                                                                  |
|---------------------------|--------|------|------------------------------------------------------------------------------|
| `addresses`               | string | —    | User wallet.                                                                 |
| `sTRXBalance`             | number | sTRX | Current sTRX balance.                                                        |
| `unstakingAmount`         | number | TRX  | Amount currently in the un‑staking cooldown period.                          |
| `availableWithdrawAmount` | number | TRX  | TRX already through the cooldown and ready to withdraw.                      |

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

**Response data**

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
        "delegatedAmount":  10000.000000,
        "rentRemainAmount": 8500.000000,
        "rentAmountPerDay": 1500.000000
      }
    ]
  }
}
```

| Field              | Type   | Unit         | Description                                              |
|--------------------|--------|--------------|----------------------------------------------------------|
| `rentType`         | string | enum         | `"Energy"`. Bandwidth not exposed yet.                   |
| `renter`           | string | TRON address | The account paying the rent.                             |
| `receiver`         | string | TRON address | The account receiving the delegated Energy.              |
| `delegatedAmount`  | number | TRX          | TRX equivalent of the energy currently delegated.        |
| `rentRemainAmount` | number | TRX          | TRX prepayment still remaining for this order.           |
| `rentAmountPerDay` | number | TRX / day    | Daily TRX cost of the rental order.                      |

---

## 6. Quick reference for AI agents

If you are an LLM tool building requests against this API, follow these rules:

1. **All endpoints are `GET` against `https://openapi.just.network`.**
2. **All responses are wrapped in `{code, message, data}`. Always check `code == 0` before reading `data`.**
3. **Numbers are already de‑scaled** — never multiply by `1e18` / `1e6` again unless explicitly told (the only exception is `amount` / `index` in `/mining/distributions`, which are hex `uint256` in raw smallest units).
4. **Rates (`*Rate`, `apy`) are annualized decimals.** Multiply by 100 for `%`.
5. **A market's effective supply APY** = `tokenList[i].supplyRate` + (mining apy if `tokenList[i].address` appears in `/mining/apy`, else 0).
6. **Address‑keyed objects** — look up the jToken address in §2 to know which market a sub‑object refers to.
7. **Liquidations** — pull `/justlend/liquidate/highRiskAccountList` periodically; `risk > 1` ⇒ liquidatable.
8. **Mining claims** — every entry of `/mining/distributions` with `claimed == false` is a free transaction the user should submit.

The machine‑readable OpenAPI 3.1 spec lives at [`apis/justlend_apis.yaml`](./apis/justlend_apis.yaml) and stays consistent with this page.

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
