# JustLend Skills

**GitHub**: [https://github.com/justlend/justlend-skills](https://github.com/justlend/justlend-skills)

JustLend Skills (`@justlend/justlend-skills`) is an AI Agent skill suite for [JustLend DAO](https://justlend.org) on TRON. It provides structured instructions (Skills) and a lightweight **read-only** [MCP](https://modelcontextprotocol.io/) server that enables AI agents to query market data, monitor account positions, analyze lending risks, and explore protocol metrics.

!!! note
    This is a **read-only** query package. No write operations or transaction signing are supported. For write operations (supply, borrow, repay, withdraw, sTRX staking, energy rental, governance voting), use the full MCP server: [@justlend/mcp-server-justlend](https://github.com/justlend/mcp-server-justlend).

## Overview

The project consists of two parts:

1. **Skills** — Structured instruction guides for 4 JustLend domains (lending, sTRX staking, energy rental, governance). Skills teach AI agents the domain knowledge and workflows needed to assist users.
2. **MCP Server** — A lightweight read-only MCP server with 9 query tools for on-chain and API data retrieval.

### Skills (4 Domains)

| Skill | Description | Query Tools |
|-------|-------------|-------------|
| `justlend-lending-v1` | Supply, borrow, repay, and withdraw on JustLend markets | 9 tools included in this package |
| `justlend-trx-staking` | Stake TRX to receive sTRX liquid staking tokens | Requires full MCP server |
| `justlend-energy-rental` | Rent TRON Energy from JustLend marketplace | Requires full MCP server |
| `justlend-governance-v1` | Participate in JustLend DAO proposal voting | Requires full MCP server |

Each skill includes workflow rules, example prompts, and references to the required MCP tools. The lending skill works with the built-in query tools; the other three provide instructional guidance and require the [full MCP server](mcp_server.md) for write operations.

### Key Capabilities (Query-Only)

- **Market Data**: Real-time APYs (including mining rewards), TVL, and utilization rates for all JustLend markets
    - Direct contract queries for on-chain accuracy
    - API-based queries for comprehensive market data (more stable, includes historical data and mining rewards)
- **Protocol Dashboard**: Total supply, total borrow, TVL, user count across the protocol
- **Account Analysis**: Full position analysis with health factor monitoring, liquidation risk assessment
    - Contract-based: Health factor, available liquidity, shortfall
    - API-based: Enhanced data with mining rewards, historical trends, risk metrics
- **Token Balances**: Query native TRX and TRC20 token balances (USDT, USDD, USDC, BTC, ETH, SUN, WIN, etc.)
- **Token Allowances**: Check TRC20 approval status for JustLend contracts

## Supported Markets

| jToken | Underlying | Description |
|--------|-----------|-------------|
| jTRX   | TRX       | Native TRON token |
| jUSDT  | USDT      | Tether USD |
| jUSDD  | USDD      | Decentralized USD |
| jUSDC  | USDC      | USD Coin |
| jBTC   | BTC       | Bitcoin (TRC20) |
| jETH   | ETH       | Ethereum (TRC20) |
| jSUN   | SUN       | SUN Token |
| jWIN   | WIN       | WINkLink |

> The full MCP server supports 24+ markets including jsTRX, jwstUSDT, jWBTC, and more.

## Prerequisites

- [Node.js](https://nodejs.org/) 20.0.0 or higher
- [TronGrid API key](https://www.trongrid.io/) for blockchain read access (strongly recommended)

## Installation

```bash
git clone https://github.com/justlend/justlend-skills.git
cd justlend-skills
npm install
```

Or use the quick setup script (auto-creates `.env` interactively):

```bash
git clone https://github.com/justlend/justlend-skills.git
cd justlend-skills
bash install.sh
```

## Configuration

### Environment Variables

Create a `.env` file (or use `install.sh`):

```bash
# Required — get from https://www.trongrid.io/
TRONGRID_API_KEY=your_trongrid_api_key

# Network: mainnet (default) or nile (testnet)
NETWORK=mainnet
```

### Client Configuration

#### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "justlend": {
      "command": "node",
      "args": ["/ABSOLUTE_PATH_TO/justlend-skills/scripts/mcp_server.mjs"],
      "env": {
        "TRONGRID_API_KEY": "your_key"
      }
    }
  }
}
```

#### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "justlend": {
      "command": "node",
      "args": ["/ABSOLUTE_PATH_TO/justlend-skills/scripts/mcp_server.mjs"],
      "env": {
        "TRONGRID_API_KEY": "your_key"
      }
    }
  }
}
```

#### Claude Code

Add to `.claude/settings.local.json`:

```json
{
  "mcpServers": {
    "justlend": {
      "command": "node",
      "args": ["/ABSOLUTE_PATH_TO/justlend-skills/scripts/mcp_server.mjs"],
      "env": {
        "TRONGRID_API_KEY": "your_key"
      }
    }
  }
}
```

#### Codex CLI

Symlink skills to the Codex agents directory:

```bash
ln -s /ABSOLUTE_PATH_TO/justlend-skills ~/.agents/skills/justlend-skills
```

## Usage

**As MCP Server** (for AI agents):

```bash
npm start
```

**As CLI Tool** (for quick checks):

```bash
node scripts/justlend_api.mjs markets              # List all markets with APY
node scripts/justlend_api.mjs dashboard            # Protocol dashboard (TVL, users)
node scripts/justlend_api.mjs supported-markets    # List supported markets & addresses
node scripts/justlend_api.mjs balance <addr>       # Check TRX balance
node scripts/justlend_api.mjs balance <addr> USDT  # Check token balance
node scripts/justlend_api.mjs account <addr>       # Account health status
node scripts/justlend_api.mjs account-api <addr>   # Full account data from API
node scripts/justlend_api.mjs jtoken-details <jtoken>  # Detailed jToken info
node scripts/justlend_api.mjs allowance <addr> USDT    # Check TRC20 approval
```

## MCP Tools Reference

### Tools (9 total, all read-only)

| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_all_markets` | — | All markets with supply/borrow APY, mining rewards, and TVL |
| `get_dashboard` | — | Protocol overview: total supply, borrow, TVL, user count |
| `get_supported_markets` | — | List all supported markets with jToken/underlying addresses |
| `get_jtoken_details` | `jtokenAddr` | Detailed jToken info: interest rate model, reserves, mining rewards, utilization |
| `get_account_summary` | `address` | Health factor, available liquidity, liquidation risk |
| `get_account_data_from_api` | `address` | Comprehensive account data from API (positions, rewards, trends) |
| `get_trx_balance` | `address` | Native TRX balance |
| `get_token_balance` | `address`, `token` | TRC20 token balance (USDT, USDD, USDC, etc.) |
| `check_allowance` | `address`, `asset` | Check TRC20 approval status for JustLend contracts |

## Security

- **Read-Only**: All tools use read-only contract calls (`triggerConstantContract`) or HTTP API queries. No transaction signing or state modifications.
- **API Key Only**: Only requires a TronGrid API key for blockchain read access. No wallet or private key needed.
- **Test First**: Use Nile testnet (`NETWORK=nile`) to verify queries before mainnet.

## Example Conversations

**"What are the best supply rates on JustLend right now?"**
→ AI calls `get_all_markets`, sorts by supply APY (includes mining rewards), presents ranking

**"Show me the JustLend protocol stats"**
→ AI calls `get_dashboard`, displays total TVL, supply/borrow volume, user count

**"Am I at risk of liquidation?"**
→ AI calls `get_account_summary`, analyzes health factor, warns if < 1.5

**"Check my full position with mining rewards"**
→ AI calls `get_account_data_from_api` for comprehensive position details including rewards

**"What is the TRX balance of address TXxx...?"**
→ AI calls `get_trx_balance`, returns balance

**"How much USDT do I have?"**
→ AI calls `get_token_balance` with token=USDT, returns balance

**"Show me details for the jUSDT market"**
→ AI calls `get_jtoken_details`, returns interest rate model, reserves, utilization, mining rewards
