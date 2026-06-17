---
title: AI / LLMs entry points
description: Machine-readable documentation endpoints for AI agents — /llms.txt, /llms-full.txt, OpenAPI 3.1 YAML, contracts.json, JSON ABIs. Includes precision and source-of-truth guidance.
---

# AI / LLMs

JustLend DAO provides machine-readable documentation endpoints optimized for LLMs and AI coding tools. Use these resources to give your AI assistant accurate, up-to-date context about the JustLend protocol.

## Available endpoints

| File | Description |
|------|-------------|
| [`llms.txt`](/llms.txt) | Curated index of key pages with one-line descriptions. Start here for quick lookups and scoped questions. |
| [`llms-full.txt`](/llms-full.txt) | Condensed full-text snapshot of the documentation for single-fetch LLM consumption. Use when your tool supports larger context. |
| [`documents/aidocs`](../documents/aidocs/index.md) | Compact AI/RAG-oriented pages with source-of-truth rules, tool mappings, safety policy, Chinese/English FAQs, and MCP tool catalog. |

!!! tip "Machine-readable sources"
    For API and contract integrations, also prefer the [OpenAPI spec](../developers/apis/justlend_apis.yaml), [contract directory](../developers/contracts.json), [contract directory JSON Schema](../developers/contracts.schema.json), and JSON ABI files under [`/developers/abis/`](../developers/abis/jtoken.json).

## Which file should I use?

| Use case | Recommended |
|----------|-------------|
| Quick lookups, scoped questions, page discovery | [`llms.txt`](/llms.txt) |
| Full protocol understanding, complex integrations, offline ingestion | [`llms-full.txt`](/llms-full.txt) |
| RAG chunks, benchmark questions, Chinese/English user intent routing | [`documents/aidocs`](../documents/aidocs/index.md) |
| Public HTTP API calls and response schemas | [`justlend_apis.yaml`](../developers/apis/justlend_apis.yaml) |
| Contract addresses in Base58 / EVM hex / TRON hex | [`contracts.json`](../developers/contracts.json) |
| Validating a copy of `contracts.json` (schema check) | [`contracts.schema.json`](../developers/contracts.schema.json) (JSON Schema 2020-12) |
| Contract calls, event decoding, and agent tooling | [`developers/abis/`](../developers/abis/jtoken.json) |
| MCP tool routing and safety annotations | [`MCP Tool Catalog`](../documents/aidocs/mcp_tools.md) |


## AI Docs scoring and retrieval hints

The [`documents/aidocs`](../documents/aidocs/index.md) section is intentionally more repetitive and task-oriented than the human docs. It is designed for RAG scoring, benchmark questions, and agent routing:

- each page has frontmatter `title`, `description`, and `tags`;
- each page answers one narrow intent such as market data, account position, lending action, sTRX staking, or energy rental;
- safety-sensitive workflows link to the MCP safety policy before any write action;
- Chinese and English common questions are mapped to the same source-of-truth tools.

## Notes for agents

- Treat the OpenAPI spec, MCP tools, `contracts.json`, and ABI JSON files as machine-readable sources of truth.
- Treat rendered pages as human-readable explanations and examples.
- Respect documented precision rules: jTokens use 8 decimals; underlying assets use their own decimals; rates and mantissas are scaled by `1e18`.
- Use Nile testnet for integration testing and Mainnet only when users explicitly intend production transactions.
