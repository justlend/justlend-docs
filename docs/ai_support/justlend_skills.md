# JustLend Skills

**GitHub**: [https://github.com/justlend/justlend-skills](https://github.com/justlend/justlend-skills)

JustLend Skills (`@justlend/justlend-skills`) is an AI Agent skills package for the **JustLend DAO** protocol on TRON. It provides structured skill instructions and a lightweight [MCP server](https://modelcontextprotocol.io/) (15 tools) that enables AI agents (Claude Code, Claude Desktop, Cursor, Codex, etc.) to query market data, manage lending positions, and execute DeFi operations.

It also works as a standalone **CLI tool** for quick market checks and lending operations directly from the terminal.

!!! note
    For advanced features (sTRX staking, energy rental, governance voting, 54 tools, 24+ markets), use the full MCP server: [@justlend/mcp-server-justlend](mcp_server.md).

## Overview

[JustLend DAO](https://justlend.org) is the largest lending protocol on TRON, based on the Compound V2 architecture. JustLend Skills wraps the core lending functionality into MCP tools and structured skill instructions that AI agents can use.

### Key Capabilities

- **Market Data**: Real-time APYs (including mining rewards), TVL, utilization rates for all markets
- **Protocol Dashboard**: Total supply, borrow volume, TVL, and user count across the protocol
- **Account Analysis**: Health factor monitoring, liquidation risk assessment, balance queries
- **Lending Operations**: Supply assets, borrow against collateral, repay loans, withdraw positions
- **Token Approvals**: Check and manage TRC20 approvals for JustLend contracts

### Skill Modules

The project includes 4 structured skill modules in the `/skills` directory that provide AI agents with domain-specific instructions and workflows:

| Skill | Description | MCP Server Required |
|-------|-------------|---------------------|
| **justlend-lending-v1** | Supply, borrow, repay, withdraw workflows with health factor monitoring | JustLend Skills (built-in) |
| **justlend-trx-staking** | Stake TRX for sTRX liquid staking tokens | Full MCP Server |
| **justlend-energy-rental** | Rent TRON Energy at discounted rates (50-80% cheaper) | Full MCP Server |
| **justlend-governance-v1** | View proposals, deposit JST for voting power, cast votes | Full MCP Server |

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
- A **burner wallet** private key for write operations — **never use your main wallet**

## Installation

```bash
git clone https://github.com/justlend/justlend-skills.git
cd justlend-skills
bash install.sh
```

Or manually:

```bash
npm install
cp .env.example .env   # Then edit .env with your keys
```

## Configuration

Edit `.env`:

```env
# Required — get from https://www.trongrid.io/
TRONGRID_API_KEY=your_trongrid_api_key

# Required for write operations (supply, borrow, repay, etc.)
# SECURITY: Use a BURNER WALLET — never your main wallet!
TRON_PRIVATE_KEY=your_burner_wallet_private_key

# Network: mainnet (default) or nile (testnet)
NETWORK=mainnet
```

!!! warning
    Always use a **dedicated burner wallet** with minimal funds. Never configure your main wallet's private key. Omit `TRON_PRIVATE_KEY` entirely for read-only mode.

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
        "TRONGRID_API_KEY": "your_key",
        "TRON_PRIVATE_KEY": "your_burner_key"
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
        "TRONGRID_API_KEY": "your_key",
        "TRON_PRIVATE_KEY": "your_burner_key"
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
        "TRONGRID_API_KEY": "your_key",
        "TRON_PRIVATE_KEY": "your_burner_key"
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

The server communicates over stdio and exposes 15 MCP tools.

### CLI Tool Mode

For quick checks and operations directly from the terminal:

```bash
# Market data
node scripts/justlend_api.mjs markets              # List all markets with APY
node scripts/justlend_api.mjs dashboard            # Protocol dashboard (TVL, users)
node scripts/justlend_api.mjs supported-markets    # List supported markets & addresses

# Account queries
node scripts/justlend_api.mjs address              # Show wallet address
node scripts/justlend_api.mjs balance <addr>       # Check TRX balance
node scripts/justlend_api.mjs balance <addr> USDT  # Check token balance
node scripts/justlend_api.mjs account <addr>       # Account health status
node scripts/justlend_api.mjs account-api <addr>   # Full account data from API
node scripts/justlend_api.mjs jtoken-details <jtoken>  # Detailed jToken info
node scripts/justlend_api.mjs allowance <addr> USDT    # Check TRC20 approval

# Write operations
node scripts/justlend_api.mjs supply TRX 10        # Supply 10 TRX
node scripts/justlend_api.mjs approve USDT 1000    # Approve 1000 USDT
```

## Skills Reference

### JustLend Lending (justlend-lending-v1)

Core lending skill providing supply, borrow, repay, and withdraw workflows with built-in health factor monitoring and TRC20 approval handling.

**Workflow Rules:**

1. **Always check before acting** — use `get_all_markets` for APYs, `get_account_summary` for health factor, and `get_trx_balance` / `get_token_balance` to verify funds
2. **TRC20 approval required** — before `supply` or `repay` for TRC20 tokens, call `check_allowance` then `approve_underlying` if needed. Native TRX needs no approval.
3. **Post-operation verification** — call `get_account_summary` after any write operation to confirm success

**Typical Workflow — Supply TRC20 (e.g., USDT):**

1. `get_token_balance` — verify sufficient funds
2. `check_allowance` — check if already approved
3. `approve_underlying` — approve if needed
4. `supply` — deposit USDT
5. `get_account_summary` — confirm position updated

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

### Read-Only Tools

| Tool | Inputs | Description |
|------|--------|-------------|
| `get_all_markets` | — | All markets with supply/borrow APY, mining rewards, and TVL |
| `get_dashboard` | — | Protocol overview: total supply, borrow, TVL, user count |
| `get_supported_markets` | — | List all supported markets with jToken/underlying addresses |
| `get_jtoken_details` | `jtokenAddr` | Detailed jToken info: interest rate model, reserves, mining rewards |
| `get_wallet_address` | — | Currently configured wallet address |
| `get_account_summary` | `address` | Health factor, liquidity, liquidation risk |
| `get_account_data_from_api` | `address` | Comprehensive account data from API (positions, rewards) |
| `get_trx_balance` | `address` | Native TRX balance |
| `get_token_balance` | `address`, `token` | TRC20 token balance (USDT, USDD, etc.) |
| `check_allowance` | `address`, `asset` | Check TRC20 approval status for JustLend contracts |

### Write Operations

| Tool | Inputs | Description |
|------|--------|-------------|
| `approve_underlying` | `asset`, `amount?` | Approve TRC20 for JustLend (required before supply/repay for TRC20 tokens) |
| `supply` | `asset`, `amount` | Deposit assets (TRX or TRC20) to earn interest |
| `withdraw` | `asset`, `amount` | Redeem supplied assets |
| `borrow` | `asset`, `amount` | Borrow against collateral |
| `repay` | `asset`, `amount` | Repay outstanding loans |

## Security Considerations

- **Burner Wallet Only**: Always use a dedicated wallet with minimal funds for AI interactions. Never use your main wallet.
- **Read-Only Mode**: Omit `TRON_PRIVATE_KEY` from `.env` to restrict the agent to read-only operations.
- **Private Keys**: Stored only in `.env` (gitignored), never exposed via MCP tools or AI conversation logs.
- **Test First**: Use Nile testnet (`NETWORK=nile`) before mainnet operations.
- **Health Factor**: Always check account health before borrowing. If `shortfallUSD > 0`, the position is at liquidation risk.
- **Gas**: Keep at least 50-100 TRX in the wallet for transaction fees (Energy and Bandwidth).

## Example Conversations

**"What are the best supply rates on JustLend?"**
→ AI calls `get_all_markets`, sorts by totalSupplyAPY (includes mining rewards), presents ranking

**"Show me the JustLend protocol stats"**
→ AI calls `get_dashboard`, displays total TVL, supply/borrow volume, user count

**"Check if my position is safe"**
→ AI calls `get_account_data_from_api` for full position details, analyzes health factor

**"Supply 1000 USDT to JustLend"**
→ AI checks balance → `check_allowance` → if needed `approve_underlying` → `supply` → confirms

**"Repay 100 TRX borrow"**
→ AI calls `repay` directly (TRX needs no approval)

**"What markets have mining rewards?"**
→ AI calls `get_all_markets`, filters by miningAPY > 0, presents markets with active rewards

**"Show me detailed info for the jUSDT market"**
→ AI calls `get_jtoken_details` with jUSDT address, displays interest rate model, reserves, and mining rewards

## Troubleshooting

### `OUT_OF_ENERGY` or `BANDWIDTH_ERROR`

The wallet needs TRX to pay for transaction fees. Ensure at least 50-100 TRX is available in the wallet.

### `REVERT` on Supply/Repay

TRC20 tokens (USDT, USDD) require approval before the JustLend contract can move them. Call `approve_underlying` first. Native TRX does not need approval.

### `exit_market` Failure

Cannot disable collateral if it would push health factor below 1.0. Repay debt or add more collateral first.

### Private Key Not Configured

Write operations require `TRON_PRIVATE_KEY` in `.env`. Run `bash install.sh` to set up the environment, or manually edit `.env`.

### TronGrid API Errors

Verify your `TRONGRID_API_KEY` is valid and not rate-limited. Get a key from [trongrid.io](https://www.trongrid.io/).
