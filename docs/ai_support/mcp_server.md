# MCP Server

**GitHub**: [https://github.com/justlend/justlend-skills](https://github.com/justlend/justlend-skills)

The JustLend Skills MCP Server is a [Model Context Protocol](https://modelcontextprotocol.io/) server that enables AI agents to query **JustLend DAO** protocol data on TRON. Check market rates, monitor account positions, analyze lending risks, and explore protocol metrics — all through a unified AI interface.

!!! note
    This is a **read-only** query server. No write operations or transaction signing are supported. For advanced features (supply, borrow, repay, withdraw, sTRX staking, energy rental, governance voting), use the full MCP server: [@justlend/mcp-server-justlend](https://github.com/justlend/mcp-server-justlend).

## Overview

[JustLend DAO](https://justlend.org) is the largest lending protocol on TRON, based on the Compound V2 architecture. This MCP server exposes read-only query tools that AI agents (Claude Desktop, Claude Code, Cursor, Codex, etc.) can use to retrieve market data, check account positions, and analyze DeFi lending information.

### Key Capabilities

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
cp .env.example .env   # Then edit .env with your keys
```

Or use the quick setup script:

```bash
git clone https://github.com/justlend/justlend-skills.git
cd justlend-skills
bash install.sh
```

## Configuration

### Environment Variables

Edit `.env`:

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

## API Reference

### Tools (9 total, all read-only)

| Tool | Description |
|------|-------------|
| `get_all_markets` | All markets with supply/borrow APY, mining rewards, and TVL |
| `get_dashboard` | Protocol overview: total supply, borrow, TVL, user count |
| `get_supported_markets` | List all supported markets with jToken/underlying addresses |
| `get_jtoken_details` | Detailed jToken info: interest rate model, reserves, mining rewards, utilization |
| `get_account_summary` | Health factor, available liquidity, liquidation risk |
| `get_account_data_from_api` | Comprehensive account data from API (positions, rewards, trends) |
| `get_trx_balance` | Native TRX balance |
| `get_token_balance` | TRC20 token balance (USDT, USDD, USDC, etc.) |
| `check_allowance` | Check TRC20 approval status for JustLend contracts |

## Security

- **Read-Only**: This server only provides query functionality. No write operations or transaction signing.
- **API Key Only**: Only requires a TronGrid API key for blockchain read access.
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
