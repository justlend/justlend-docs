---
title: Resolving Contract Addresses
description: How to look up JustLend jToken, underlying, and Moolah market identifiers from contracts.json and the public REST API on TRON mainnet and Nile testnet.
---

# Resolving Contract Addresses

!!! info "About this page"
    **Protocol:** JustLend DAO · **Network:** TRON (Mainnet + Nile) · **Scope:** map human-facing symbols (`jUSDT`, `USDT`, Moolah vault names) to on-chain Base58 / hex addresses without hard-coding. Use this when integrating lending flows, MCP tools, or indexers that need stable identifiers.

## Machine-readable registry

[`contracts.json`](contracts.json) is the canonical address book. Each entry includes:

| Field | Use |
|-------|-----|
| `symbol` | Human label (`jUSDT`, `USDT`, `Moolah TRX Vault`) |
| `type` | `jToken`, `underlying`, `comptroller`, `moolah-vault`, `moolah-market`, … |
| `network` | `mainnet` or `nile` |
| `address.base58` | TRON Base58 (`T…`) for TronWeb `.send()` / `.call()` |
| `address.evm` | `0x…` hex for ABI tooling |
| `address.tronHex` | `41…` internal hex |
| `status` | `active` or `legacy` (filter to `active` for new integrations) |

### Example: jToken from underlying symbol

```javascript
import contracts from './contracts.json' assert { type: 'json' };

function jTokenForUnderlying(underlyingSymbol, network = 'mainnet') {
  const underlying = contracts.find(
    (c) => c.type === 'underlying' && c.symbol === underlyingSymbol && c.network === network
  );
  if (!underlying) throw new Error(`Unknown underlying: ${underlyingSymbol}`);

  const jtoken = contracts.find(
    (c) =>
      c.type === 'jToken' &&
      c.network === network &&
      c.underlying === underlying.symbol &&
      c.status === 'active'
  );
  if (!jtoken) throw new Error(`No active jToken for ${underlyingSymbol}`);
  return jtoken.address.base58;
}

// jUSDT on mainnet
console.log(jTokenForUnderlying('USDT'));
```

## REST API fallback

When you need live APY/TVL alongside addresses, call the public market list (see [APIs §1](apis.md#1-market-list)) and join on `jtokenAddress` or `underlyingAddress`. The MCP server uses contract queries first with this API as fallback for reliability.

## Moolah V2 identifiers

Isolated markets are keyed by `MarketParams`: `(loanToken, collateralToken, oracle, irm, lltv)`. Vault entries in `contracts.json` list the ERC-4626 share token; market tuples are documented in [SBM V2](supply_and_borrow_market/sbmV2.md). Resolve loan/collateral addresses with the same registry before constructing calldata.

## Related pages

- [Contracts Overview](contracts_overview.md)
- [Common Pitfalls](common_pitfalls.md)
- [MCP Server](../ai_support/mcp_server.md)
