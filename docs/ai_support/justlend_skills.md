# JustLend Skills

**GitHub**: [https://github.com/justlend/justlend-skills](https://github.com/justlend/justlend-skills)

JustLend Skills (`@justlend/justlend-skills`) is an AI Agent skills package for the **JustLend DAO** protocol on TRON. It provides structured skill instructions and a lightweight **read-only** [MCP server](https://modelcontextprotocol.io/) (9 query tools) that enables AI agents (Claude Code, Claude Desktop, Cursor, Codex, etc.) to query market data, monitor account positions, and analyze DeFi lending information.

It also works as a standalone **CLI tool** for quick market checks directly from the terminal.

!!! note
    This is a **read-only** query package. No write operations or transaction signing are supported. For write operations (supply, borrow, repay, withdraw, sTRX staking, energy rental, governance voting), use the full MCP server: [@justlend/mcp-server-justlend](mcp_server.md).

## Overview

[JustLend DAO](https://justlend.org) is the largest lending protocol on TRON, based on the Compound V2 architecture. JustLend Skills wraps the core query functionality into MCP tools and structured skill instructions that AI agents can use.

### Key Capabilities

- **Market Data**: Real-time APYs (including mining rewards), TVL, utilization rates for all markets
- **Protocol Dashboard**: Total supply, borrow volume, TVL, and user count across the protocol
- **Account Analysis**: Health factor monitoring, liquidation risk assessment, balance queries
- **Token Balances**: Query native TRX and TRC20 token balances (USDT, USDD, USDC, BTC, ETH, SUN, WIN, etc.)
- **Token Allowances**: Check TRC20 approval status for JustLend contracts

### Skill Modules

The project includes 4 structured skill modules in the `/skills` directory that provide AI agents with domain-specific instructions and workflows:

| Skill | Description | MCP Server Required |
|-------|-------------|---------------------|
| **justlend-lending-v1** | Market queries, account analysis, health factor monitoring | JustLend Skills (built-in) |
| **justlend-trx-staking** | Stake TRX for sTRX liquid staking tokens | Full MCP Server |
| **justlend-energy-rental** | Rent TRON Energy at discounted rates (50-80% cheaper) | Full MCP Server |
| **justlend-governance-v1** | View proposals, deposit JST for voting power, cast votes | Full MCP Server |

The lending skill works with the built-in 9 query tools. The other three skills provide instructional guidance and require the [full MCP server](mcp_server.md) for write operations.

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

!!! tip
    The full MCP server supports 24+ markets including jsTRX, jwstUSDT, jWBTC, and more.

## Prerequisites

- [Node.js](https://nodejs.org/) 20.0.0 or higher
- [TronGrid API key](https://www.trongrid.io/) (required)

## Installation

```bash
git clone https://github.com/justlend/justlend-skills.git
cd justlend-skills
bash install.sh
```

Or manually:

```bash
npm install
```

The `install.sh` script will create `.env` and prompt for your TronGrid API key.

## Configuration

Create a `.env` file (or use `install.sh`):

```env
# Required — get from https://www.trongrid.io/
TRONGRID_API_KEY=your_trongrid_api_key

# Network: mainnet (default) or nile (testnet)
NETWORK=mainnet
```

### Client Configuration

#### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

```bash
git clone https://github.com/justlend/justlend-skills ~/.codex/justlend-skills
cd ~/.codex/justlend-skills && bash install.sh
mkdir -p ~/.agents/skills
ln -s ~/.codex/justlend-skills/skills ~/.agents/skills/justlend-skills
```

## Usage

### MCP Server Mode

For AI agent integrations (Claude Desktop, Cursor, Claude Code, etc.):

```bash
npm start
```

The server communicates over stdio and exposes 9 read-only MCP tools.

### CLI Tool Mode

For quick checks directly from the terminal:

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

## Skills Reference

### JustLend Lending (justlend-lending-v1)

Core lending skill providing market queries, account analysis, and health factor monitoring workflows.

**Workflow Rules:**

1. **Always check before advising** — use `get_all_markets` for APYs, `get_account_summary` for health factor, and `get_trx_balance` / `get_token_balance` to verify balances
2. **TRC20 approval awareness** — use `check_allowance` to check approval status before recommending supply or repay operations
3. **Risk assessment** — call `get_account_summary` to evaluate liquidation risk; warn if `shortfallUSD > 0`

### sTRX Staking (justlend-trx-staking)

Liquid staking skill for TRX. Stake TRX to receive sTRX tokens that earn staking rewards automatically while remaining usable in DeFi.

!!! note
    This skill requires the [full MCP server](mcp_server.md) for tool execution.

**How it works:** Deposit TRX → receive sTRX → rewards accrue via exchange rate appreciation → unstake with ~14 day unbonding period.

### Energy Rental (justlend-energy-rental)

Rent TRON Energy from the JustLend marketplace at 50-80% lower cost than burning TRX for transaction fees.

!!! note
    This skill requires the [full MCP server](mcp_server.md) for tool execution.

### DAO Governance (justlend-governance-v1)

Participate in JustLend DAO governance proposals. Deposit JST for voting power (1 JST = 1 Vote), cast votes, and reclaim votes after proposals end.

!!! note
    This skill requires the [full MCP server](mcp_server.md) for tool execution.

**Voting Workflow:**

1. `get_proposal_list` — find active proposals
2. `get_vote_info` — check available voting power
3. If no votes: `approve_jst_for_voting` → `deposit_jst_for_votes`
4. `cast_vote` — vote FOR or AGAINST
5. After proposal ends: `withdraw_votes_from_proposal` → `withdraw_votes_to_jst`

## MCP Tools Reference

### Tools (9 total, all read-only)

| Tool | Inputs | Description |
|------|--------|-------------|
| `get_all_markets` | — | All markets with supply/borrow APY, mining rewards, and TVL |
| `get_dashboard` | — | Protocol overview: total supply, borrow, TVL, user count |
| `get_supported_markets` | — | List all supported markets with jToken/underlying addresses |
| `get_jtoken_details` | `jtokenAddr` | Detailed jToken info: interest rate model, reserves, mining rewards |
| `get_account_summary` | `address` | Health factor, liquidity, liquidation risk |
| `get_account_data_from_api` | `address` | Comprehensive account data from API (positions, rewards) |
| `get_trx_balance` | `address` | Native TRX balance |
| `get_token_balance` | `address`, `token` | TRC20 token balance (USDT, USDD, etc.) |
| `check_allowance` | `address`, `asset` | Check TRC20 approval status for JustLend contracts |

## Security

- **Read-Only**: All tools use read-only contract calls (`triggerConstantContract`) or HTTP API queries. No transaction signing or state modifications.
- **API Key Only**: Only requires a TronGrid API key for blockchain read access. No wallet or private key needed.
- **Test First**: Use Nile testnet (`NETWORK=nile`) to verify queries before mainnet.

## Example Conversations

**"What are the best supply rates on JustLend?"**
→ AI calls `get_all_markets`, sorts by supply APY (includes mining rewards), presents ranking

**"Show me the JustLend protocol stats"**
→ AI calls `get_dashboard`, displays total TVL, supply/borrow volume, user count

**"Check if my position is safe"**
→ AI calls `get_account_summary`, analyzes health factor, warns if `shortfallUSD > 0`

**"Check my full position with mining rewards"**
→ AI calls `get_account_data_from_api` for comprehensive position details including rewards

**"What is the TRX balance of address TXxx...?"**
→ AI calls `get_trx_balance`, returns balance

**"How much USDT do I have?"**
→ AI calls `get_token_balance` with token=USDT, returns balance

**"Show me detailed info for the jUSDT market"**
→ AI calls `get_jtoken_details`, returns interest rate model, reserves, utilization, mining rewards

**"What markets have mining rewards?"**
→ AI calls `get_all_markets`, filters by miningAPY > 0, presents markets with active rewards

## Troubleshooting

### TronGrid API Errors

Verify your `TRONGRID_API_KEY` is valid and not rate-limited. Get a key from [trongrid.io](https://www.trongrid.io/).

### Invalid Address

Ensure the address is a valid TRON base58 address (starts with `T`, 34 characters).
