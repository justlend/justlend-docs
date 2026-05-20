# AI / LLMs

JustLend DAO provides machine-readable documentation endpoints optimized for LLMs and AI coding tools. Use these resources to give your AI assistant accurate, up-to-date context about the JustLend protocol.

## Available endpoints

| File | Description |
|------|-------------|
| [`llms.txt`](/llms.txt) | Curated index of key pages with one-line descriptions. Start here for quick lookups and scoped questions. |
| [`llms-full.txt`](/llms-full.txt) | Condensed full-text snapshot of the documentation for single-fetch LLM consumption. Use when your tool supports larger context. |

!!! tip "Machine-readable sources"
    For API and contract integrations, also prefer the [OpenAPI spec](../developers/apis/justlend_apis.yaml), [contract directory](../developers/contracts.json), and JSON ABI files under [`/developers/abis/`](../developers/abis/jtoken.json).

## Which file should I use?

| Use case | Recommended |
|----------|-------------|
| Quick lookups, scoped questions, page discovery | [`llms.txt`](/llms.txt) |
| Full protocol understanding, complex integrations, offline ingestion | [`llms-full.txt`](/llms-full.txt) |
| Public HTTP API calls and response schemas | [`justlend_apis.yaml`](../developers/apis/justlend_apis.yaml) |
| Contract addresses in Base58 / EVM hex / TRON hex | [`contracts.json`](../developers/contracts.json) |
| Contract calls, event decoding, and agent tooling | [`developers/abis/`](../developers/abis/jtoken.json) |

## Notes for agents

- Treat the OpenAPI spec, MCP tools, `contracts.json`, and ABI JSON files as machine-readable sources of truth.
- Treat rendered pages as human-readable explanations and examples.
- Respect documented precision rules: jTokens use 8 decimals; underlying assets use their own decimals; rates and mantissas are scaled by `1e18`.
- Use Nile testnet for integration testing and Mainnet only when users explicitly intend production transactions.
