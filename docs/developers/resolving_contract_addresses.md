---
title: Resolving Contract Addresses
description: How to look up JustLend jToken and deployed-contract addresses from the machine-readable registry on TRON mainnet and Nile testnet.
---

# Resolving Contract Addresses

!!! info "About this page"
    **Protocol:** JustLend DAO · **Network:** TRON (Mainnet + Nile) · **Scope:** map human-facing symbols (`jUSDT`, `USDT`, and other contract labels) to on-chain Base58 and hexadecimal addresses without hard-coding them in an integration.

## Machine-readable registry

[`contracts.json`](contracts.json) is the canonical address registry. The root object contains a `networks` map, and each network contains optional contract categories such as `jtokens`, `comptroller`, `governance`, `strx`, and `interest_rate_models`.

### Address formats

Every deployed-contract address uses the same three fields:

| Field | Use |
|-------|-----|
| `address.base58` | TRON Base58Check (`T…`) for wallets, Tronscan, and TronWeb |
| `address.hex_evm` | EVM-style `0x…` address for ABI and cross-chain tooling |
| `address.hex_tron` | TRON-internal `0x41…` address for low-level TronGrid/TronWeb calls |

### jToken records

For a network that exposes SBM markets, jTokens are keyed by symbol at `networks.<network>.jtokens.<symbol>`. A jToken record contains `symbol`, `status`, `underlying_symbol`, decimal metadata, nested `delegator` and `underlying` records, and, when applicable, a `delegate` contract record. Native TRX has no TRC20 underlying address, so its `underlying` record contains a note instead.

Filter `status === "active"` before directing new supply or borrow positions. Legacy markets remain queryable for unwinding existing positions but are closed to new supply and borrow.

### Example: resolve a jToken from its underlying symbol

```javascript
import contracts from './contracts.json' with { type: 'json' };

function jTokenForUnderlying(underlyingSymbol, network = 'mainnet') {
  const jtokens = contracts.networks?.[network]?.jtokens ?? {};
  const jtoken = Object.values(jtokens).find(
    (entry) =>
      entry.underlying_symbol === underlyingSymbol &&
      entry.status === 'active'
  );

  if (!jtoken) {
    throw new Error(`No active jToken for ${underlyingSymbol} on ${network}`);
  }

  return {
    symbol: jtoken.symbol,
    jTokenAddress: jtoken.delegator.address.base58,
    jTokenHex: jtoken.delegator.address.hex_tron,
    underlyingAddress: jtoken.underlying?.address?.base58 ?? null,
  };
}

console.log(jTokenForUnderlying('USDT'));
```

The returned `underlyingAddress` is `null` for native TRX. Use the nested `delegator` address as the jToken address. When present, the `delegate` address is the upgradeable implementation and is not the user-facing market address.

## Live market data fallback

Use the public market list (`GET https://openapi.just.network/lend/jtoken`, documented in [APIs §3.1](apis.md#31-get-lendjtoken-list-all-sbm-markets)) when you also need live rates, balances, prices, or collateral factors. Join `response.data.tokenList[].address` with `networks.<network>.jtokens.*.delegator.address.base58`. For TRC20 markets, `underlyingAddress` can also be matched with `networks.<network>.jtokens.*.underlying.address.base58`; do not use this fallback for native TRX, whose API response uses the TRON zero address while the registry has no underlying address. Do not replace the registry's static contract addresses with an unverified API response.

## JustLend V2 (Moolah)

The current `contracts.json` registry is for deployed protocol contracts and SBM jTokens; it does not enumerate the live Moolah vault and isolated-market catalog. Resolve those identifiers through the documented V2 read endpoints in [APIs §3.4](apis.md#34-justlend-v2-moolah-read-endpoints), then use the returned `vaultAddress` or market `id` when constructing requests.

## Related pages

- [Contracts Overview](contracts_overview.md)
- [Common Pitfalls](common_pitfalls.md)
- [MCP Server](../ai_support/mcp_server.md)
