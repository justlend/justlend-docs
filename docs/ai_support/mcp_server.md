# MCP Server

**GitHub**: [https://github.com/justlend/mcp-server-justlend](https://github.com/justlend/mcp-server-justlend)

The JustLend MCP Server (`@justlend/mcp-server-justlend`) is a [Model Context Protocol](https://modelcontextprotocol.io/) server that enables AI agents to interact with the **JustLend DAO** protocol on TRON. Supply assets, borrow against collateral, manage positions, rent energy, stake TRX for sTRX, and analyze DeFi portfolios — all through a unified AI interface.

Beyond JustLend-specific operations, the server also exposes a full set of **general-purpose TRON chain utilities** — balance queries, block/transaction data, token metadata, TRX transfers, smart contract reads/writes, staking (Stake 2.0), multicall, and more.

!!! note
    Current version (**v1.0.5**) supports **JustLend V1** protocol. All contract addresses, ABIs, calculation functions, and lending operations are for V1.

## Overview

[JustLend DAO](https://justlend.org) is the largest lending protocol on TRON, based on the Compound V2 architecture. This MCP server wraps the full protocol functionality into tools and guided prompts that local MCP clients such as Claude Desktop, Claude Code, and Cursor can use.

### Key Capabilities

**JustLend Protocol**

- **Market Data**: Real-time APYs, TVL, utilization rates, prices for all markets
    - Smart fallback: contract queries first, API fallback for reliability
    - TTL caching (30–60s) to reduce RPC calls
- **Account Data**: Full position analysis via Multicall3 batch queries (~2.5s vs ~8s legacy)
    - Health factor, collateral, borrow positions
    - On-chain Oracle prices with API fallback
- **Batch Wallet Balances**: Query all TRC20 token balances in a single Multicall3 RPC call
- **Mining Rewards**: Advanced mining reward calculation
    - Detailed breakdown by market and reward token (USDD, TRX, WBTC, etc.)
    - Separates new period vs. last period rewards
    - USD value calculation with live token prices
    - Mining status tracking (ongoing/paused/ended) and period end times
- **Supply**: Deposit TRX or TRC20 tokens to earn interest (mint jTokens)
- **Borrow**: Borrow assets against your collateral with health factor monitoring
- **Repay**: Repay outstanding borrows with full or partial amounts
- **Withdraw**: Redeem jTokens back to underlying assets
- **Collateral Management**: Enter/exit markets, manage what counts as collateral
- **Portfolio Analysis**: AI-guided risk assessment, health factor monitoring, optimization
- **Token Approvals**: Manage TRC20 approvals for jToken contracts
- **Energy Cost Estimation**: Estimate energy, bandwidth, and TRX cost for any lending operation before executing
- **JST Voting / Governance**: View proposals, cast votes, deposit/withdraw JST for voting power, reclaim votes
- **Energy Rental**: Rent energy from JustLend, calculate rental prices, query rental orders, return/cancel rentals
- **sTRX Staking**: Stake TRX to receive sTRX, unstake sTRX, claim staking rewards, check withdrawal eligibility

**Browser Wallet Signing**

- **TronLink Integration**: Connect TronLink or other browser wallets via `tronlink-signer` SDK
- **Sign-only mode**: Server builds transactions, browser only signs — private keys never leave the wallet
- **Dual wallet mode**: Users choose between `browser` (recommended) or `agent` (encrypted local storage)

**General TRON Chain**

- **Balances**: TRX balance (with Sun/TRX conversion), TRC20/TRC1155 token balances
- **Blocks**: Latest block, block by number/hash, block number, chain ID
- **Transactions**: Fetch transaction details, receipts, wait for confirmation
- **Contracts**: Read/write any contract, fetch on-chain ABI, multicall (v2 & v3), deploy, estimate energy
- **Token Metadata**: TRC20 info (name/symbol/decimals/supply), TRC721 metadata, TRC1155 URI
- **Transfers**: Send TRX, transfer TRC20 tokens, approve spenders
- **Staking (Stake 2.0)**: Freeze/unfreeze TRX for BANDWIDTH or ENERGY, withdraw expired unfreeze
- **Address Utilities**: Hex ↔ Base58 conversion, address validation, resolution
- **Wallet**: Sign messages, secure key management via agent-wallet or browser wallet

## Supported Markets

The protocol exposes 22 jToken markets in total (16 active + 6 paused legacy markets). Call `get_supported_markets` for the live list with addresses. The active markets are:

| jToken     | Underlying | Description |
|------------|-----------|-------------|
| jTRX       | TRX       | Native TRON token |
| jUSDT      | USDT      | Tether USD |
| jUSDD      | USDD      | Decentralized USD (USDD/TRX dual-mining rewards) |
| jUSD1      | USD1      | World Liberty Financial USD |
| jTUSD      | TUSD      | TrueUSD |
| jwstUSDT   | wstUSDT   | Wrapped staked USDT (yields underlying staking APY) |
| jsTRX      | sTRX      | Staked TRX (yields underlying staking APY) |
| jBTC       | BTC       | Bitcoin (wrapped) |
| jWBTC      | WBTC      | Wrapped Bitcoin |
| jETH       | ETH       | Ethereum (wrapped) |
| jETHB      | ETHB      | Bridged Ethereum |
| jSUN       | SUN       | SUN token |
| jJST       | JST       | JUST governance token |
| jWIN       | WIN       | WINkLink |
| jBTT       | BTT       | BitTorrent token |
| jNFT       | NFT       | APENFT |

## Prerequisites

- [Node.js](https://nodejs.org/) 20.0.0 or higher
- Optional: [TronGrid API key](https://www.trongrid.io/) for reliable mainnet access (strongly recommended)

## Installation

```bash
git clone https://github.com/justlend/mcp-server-justlend.git
cd mcp-server-justlend
npm install
```

## Quick Setup

For a guided setup experience (build, configure, generate `.mcp.json`):

```bash
bash scripts/setup-mcp-test.sh
# Add --claude-desktop to also print Claude Desktop JSON
```

The script checks Node.js 20+, installs dependencies, builds the project, and generates local Claude Code config.

## Configuration

### Wallet Setup (First-Use Choice)

On first use, the server presents a wallet mode selection. Users choose between:

1. **Browser mode** (recommended): Connect TronLink via `connect_browser_wallet` — private keys never leave the browser
2. **Agent mode**: Encrypted local wallet via `set_wallet_mode` with `mode="agent"` — keys stored in `~/.agent-wallet/`

Private keys are **never** stored in environment variables by default.

You can also manage wallets via **CLI** or **MCP tools**:

#### CLI (agent-wallet)
```bash
# Import an existing private key or mnemonic
npx agent-wallet add

# Generate a new wallet
npx agent-wallet generate

# List all wallets
npx agent-wallet list

# Switch active wallet
npx agent-wallet activate <wallet-id>
```

#### MCP Tools (runtime)

| Tool | Description |
|------|-------------|
| `get_wallet_address` | Shows current address, or returns first-use wallet selection guidance |
| `connect_browser_wallet` | Connect TronLink / browser wallet for signing |
| `set_wallet_mode` | Switch between `browser` and `agent` signing |
| `get_wallet_mode` | Show current signing mode and addresses |
| `list_wallets` | List all wallets with IDs, types, addresses |
| `set_active_wallet` | Switch active wallet by ID |

Importing an existing private key is intentionally not exposed as an MCP tool because MCP arguments can be logged by clients and transports. Use the CLI instead:

```bash
npx agent-wallet import
```

### Environment Variables

```bash
# Strongly recommended — avoids TronGrid 429 rate limiting on mainnet
export TRONGRID_API_KEY="your_trongrid_api_key"

# Optional: HTTP/SSE transport mode
export MCP_TRANSPORT="http"       # Use HTTP/SSE instead of stdio
export MCP_HTTP_PORT="3000"       # HTTP server port (default: 3000)
export MCP_HTTP_HOST="127.0.0.1"  # HTTP server host (default: 127.0.0.1)

# Required in HTTP mode — Bearer token clients must send in Authorization header.
# The server refuses to start without it. Comparison is timing-safe (v1.0.5+).
export MCP_API_KEY="your_strong_random_secret"
```

### Client Configuration

Build the local server first:

```bash
npm run build
```

All local client examples below use the built stdio entrypoint:

```bash
node /absolute/path/to/mcp-server-justlend/build/index.js
```

#### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "justlend": {
      "command": "node",
      "args": ["/absolute/path/to/mcp-server-justlend/build/index.js"],
      "env": {
        "TRONGRID_API_KEY": "SET_VIA_SYSTEM_ENV"
      }
    }
  }
}
```

#### Claude Code

Add to `.mcp.json` in the project root:

```json
{
  "mcpServers": {
    "justlend": {
      "command": "node",
      "args": ["/absolute/path/to/mcp-server-justlend/build/index.js"],
      "env": {
        "TRONGRID_API_KEY": "SET_VIA_SYSTEM_ENV"
      }
    }
  }
}
```

!!! tip
    No `TRON_PRIVATE_KEY` needed — the server uses the encrypted agent-wallet or browser wallet automatically.

#### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "justlend": {
      "command": "node",
      "args": ["/absolute/path/to/mcp-server-justlend/build/index.js"],
      "env": {
        "TRONGRID_API_KEY": "SET_VIA_SYSTEM_ENV"
      }
    }
  }
}
```

## Usage

```bash
# Stdio mode (for MCP clients)
npm start

# HTTP/SSE mode (for remote clients)
npm run start:http

# Development with auto-reload
npm run dev
```

## API Reference

### Tools (59 total)

#### Wallet & Network

| Tool | Description | Write? |
|------|-------------|--------|
| `get_wallet_address` | Show wallet address or first-use wallet selection guidance | No |
| `connect_browser_wallet` | Connect TronLink / browser wallet for signing | Yes |
| `set_wallet_mode` | Switch between `browser` and `agent` signing | Yes |
| `get_wallet_mode` | Show current signing mode and addresses | No |
| `list_wallets` | List all wallets (IDs, types, addresses) | No |
| `set_active_wallet` | Switch active wallet by wallet ID | No |
| `get_supported_networks` | List available networks | No |
| `get_supported_markets` | List all jToken markets with addresses | No |
| `set_network` | Set global default network (mainnet, nile) | Yes |
| `get_network` | Get current global default network | No |

#### Market Data

| Tool | Description | Write? |
|------|-------------|--------|
| `get_market_data` | Detailed data for one market (APY, TVL, rates) — contract + API fallback | No |
| `get_all_markets` | Overview of all markets — contract + API fallback | No |
| `get_protocol_summary` | Comptroller config & protocol parameters — contract query | No |

#### Account & Balances

| Tool | Description | Write? |
|------|-------------|--------|
| `get_account_summary` | Full position: supplies, borrows, health factor — Multicall3 batch | No |
| `check_allowance` | Check TRC20 approval for jToken | No |
| `get_trx_balance` | TRX balance | No |
| `get_token_balance` | TRC20 token balance | No |
| `get_wallet_balances` | Batch-fetch TRC20 balances across multiple markets via Multicall3 | No |

#### Lending Operations

| Tool | Description | Write? |
|------|-------------|--------|
| `supply` | Deposit assets to earn interest | **Yes** |
| `withdraw` | Withdraw supplied assets | **Yes** |
| `withdraw_all` | Withdraw all from a market | **Yes** |
| `borrow` | Borrow against collateral | **Yes** |
| `repay` | Repay outstanding borrows | **Yes** |
| `enter_market` | Enable market as collateral | **Yes** |
| `exit_market` | Disable market as collateral | **Yes** |
| `approve_underlying` | Approve TRC20 for jToken | **Yes** |
| `claim_rewards` | Claim mining rewards | **Yes** |
| `estimate_lending_energy` | Estimate energy/bandwidth/TRX cost for any lending operation | No |

#### Mining & Rewards

| Tool | Description | Write? |
|------|-------------|--------|
| `get_mining_rewards` | Unclaimed mining rewards, APY, and reward breakdown | No |
| `get_usdd_mining_config` | USDD mining periods, reward tokens, and schedule | No |
| `get_wbtc_mining_config` | WBTC supply mining configuration and activity details | No |

#### JST Voting / Governance

| Tool | Description | Write? |
|------|-------------|--------|
| `get_proposal_list` | List all governance proposals with status and vote counts | No |
| `get_user_vote_status` | User's voting history: voted proposals, withdrawable votes | No |
| `get_vote_info` | Voting power: JST balance, available votes, locked votes | No |
| `get_locked_votes` | Votes locked in a specific proposal | No |
| `check_jst_allowance_for_voting` | Check JST approval for WJST voting contract | No |
| `approve_jst_for_voting` | Approve JST for the WJST voting contract | **Yes** |
| `deposit_jst_for_votes` | Deposit JST to get voting power (1 JST = 1 Vote) | **Yes** |
| `withdraw_votes_to_jst` | Withdraw WJST back to JST | **Yes** |
| `cast_vote` | Cast for/against votes on a proposal | **Yes** |
| `withdraw_votes_from_proposal` | Reclaim votes from completed proposals | **Yes** |

#### Energy Rental

| Tool | Description | Write? |
|------|-------------|--------|
| `get_energy_rental_dashboard` | Market data: TRX price, exchange rate, APY, energy per TRX | No |
| `get_energy_rental_params` | On-chain params: fees, limits, pause status, usage charge ratio | No |
| `calculate_energy_rental_price` | Estimate cost for renting energy (prepayment, deposit, daily cost) | No |
| `get_energy_rental_rate` | Current rental rate for a given TRX amount | No |
| `get_user_energy_rental_orders` | User's rental orders (as renter, receiver, or all) | No |
| `get_energy_rent_info` | On-chain rental info for a renter-receiver pair | No |
| `get_return_rental_info` | Return/cancel estimation (refund, remaining rent, daily cost) | No |
| `rent_energy` | Rent energy for a receiver (with balance, pause, limit checks) | **Yes** |
| `return_energy_rental` | Cancel an active rental (with active order check) | **Yes** |

#### sTRX Staking

| Tool | Description | Write? |
|------|-------------|--------|
| `get_strx_dashboard` | Staking market data: exchange rate, APY, total supply | No |
| `get_strx_account` | User staking account: staked amount, income, rewards | No |
| `get_strx_balance` | sTRX token balance for an address | No |
| `check_strx_withdrawal_eligibility` | Check unbonding status, pending/completed withdrawal rounds | No |
| `stake_trx_to_strx` | Stake TRX to receive sTRX (with balance check) | **Yes** |
| `unstake_strx` | Unstake sTRX to receive TRX back (with balance check) | **Yes** |
| `claim_strx_rewards` | Claim all staking rewards (with rewards existence check) | **Yes** |

#### Transfers

| Tool | Description | Write? |
|------|-------------|--------|
| `transfer_trx` | Transfer TRX to another address (with balance check) | **Yes** |
| `transfer_trc20` | Transfer TRC20 tokens by symbol or contract address | **Yes** |

### Prompts (AI-Guided Workflows)

| Prompt | Description |
|--------|-------------|
| `getting_started` | First-time onboarding: wallet setup, connection, feature tour |
| `supply_assets` | Step-by-step supply with balance checks and approval |
| `borrow_assets` | Safe borrowing with risk assessment and health factor checks |
| `repay_borrow` | Guided repayment with verification |
| `analyze_portfolio` | Comprehensive portfolio analysis with risk scoring |
| `compare_markets` | Find best supply/borrow opportunities |
| `rent_energy` | Guided energy rental with price estimation and balance checks |
| `stake_trx` | Guided TRX staking to sTRX with APY info and verification |
| `query_proposals` | Browse and query governance proposals, check voting requirements |
| `cast_vote` | Guided governance voting with vote verification |

## Security Considerations

- **Browser wallet (recommended)**: Private keys never leave TronLink — the `tronlink-signer` SDK sends unsigned transactions to the browser and receives signed results
- **Encrypted agent-wallet**: Private keys are encrypted at rest in `~/.agent-wallet/` with file permissions `0600`/`0700` — never stored in environment variables or config files
- **No key in parameters**: All signing functions use the agent-wallet or browser wallet internally; private keys are never passed as function parameters or exposed via MCP tools
- **Import via CLI**: Use `npx agent-wallet import` from a terminal — private key import is not exposed as an MCP tool to avoid key exposure in AI conversation logs
- **Write operations** are clearly marked with `destructiveHint: true` in MCP annotations
- **Health factor checks** in prompts prevent dangerous borrowing
- Always **test on Nile testnet** before mainnet operations
- Be cautious with **unlimited approvals** (`approve_underlying` with `max`)

## Example Conversations

**"What are the best supply rates on JustLend right now?"**
→ AI calls `get_all_markets`, sorts by supplyAPY, presents ranking

**"I want to supply 10,000 USDT to earn interest"**
→ AI uses `supply_assets` prompt: checks balance → approves USDT → supplies → verifies

**"Am I at risk of liquidation?"**
→ AI calls `get_account_summary`, analyzes health factor, warns if < 1.5

**"Borrow 500 USDT against my TRX collateral"**
→ AI uses `borrow_assets` prompt: checks collateral → calculates new health factor → executes if safe

**"What is the TRX balance of address TXxx...?"**
→ AI calls the general-purpose TRX balance tool, returns balance in both TRX and Sun

**"Freeze 100 TRX for ENERGY"**
→ AI calls staking service to freeze via Stake 2.0, returns transaction hash

**"Show me the latest governance proposals"**
→ AI calls `get_proposal_list`, displays proposals sorted by ID with status and vote counts

**"I want to vote for proposal #425 with 1000 JST"**
→ AI checks `get_vote_info` → if no votes, suggests `approve_jst_for_voting` + `deposit_jst_for_votes` → then `cast_vote`

**"Withdraw my votes from completed proposals"**
→ AI calls `get_user_vote_status` to find withdrawable proposals → calls `withdraw_votes_from_proposal` for each

**"How much does it cost to rent 300,000 energy for 7 days?"**
→ AI calls `calculate_energy_rental_price` with energyAmount=300000, durationHours=168, returns cost breakdown

**"Rent 500,000 energy to address TXxx... for 14 days"**
→ AI uses `rent_energy` prompt: checks balance → checks rental status → calculates price → rents energy → verifies

**"Cancel my energy rental to TXxx..."**
→ AI calls `get_energy_rent_info` to verify active rental → calls `return_energy_rental` → confirms refund

**"Stake 1000 TRX to earn sTRX rewards"**
→ AI uses `stake_trx` prompt: checks balance → checks exchange rate & APY → stakes TRX → verifies sTRX received

**"Do I have any sTRX rewards to claim?"**
→ AI calls `get_strx_account` to check claimable rewards → calls `claim_strx_rewards` if available

**"Can I withdraw my unstaked TRX?"**
→ AI calls `check_strx_withdrawal_eligibility` to check unbonding status and completed withdrawal rounds

**"Connect my TronLink wallet"**
→ AI calls `connect_browser_wallet`, opens browser window for user to approve in TronLink

**"How much energy will supplying 100 USDT cost?"**
→ AI calls `estimate_lending_energy` with operation=supply, market=jUSDT, amount=100, returns energy/bandwidth/TRX breakdown
