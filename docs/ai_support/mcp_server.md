# MCP Server

**GitHub**: [https://github.com/justlend/mcp-server-justlend](https://github.com/justlend/mcp-server-justlend)

The JustLend MCP Server (`@justlend/mcp-server-justlend`) is a [Model Context Protocol](https://modelcontextprotocol.io/) server that enables AI agents to interact with the **JustLend DAO** protocol on TRON. Supply assets, borrow against collateral, manage positions, rent energy, stake TRX for sTRX, and analyze DeFi portfolios — all through a unified AI interface.

Beyond JustLend-specific operations, the server also exposes a full set of **general-purpose TRON chain utilities** — balance queries, block/transaction data, token metadata, TRX transfers, smart contract reads/writes, staking (Stake 2.0), multicall, and more.

!!! note
    Current version (**v1.0.2**) supports **JustLend V1** protocol. All contract addresses, ABIs, calculation functions, and lending operations are for V1.

## Overview

[JustLend DAO](https://justlend.org) is the largest lending protocol on TRON, based on the Compound V2 architecture. This MCP server wraps the full protocol functionality into tools and guided prompts that AI agents (Claude Desktop, Cursor, etc.) can use.

### Key Capabilities

**JustLend Protocol**

- **Market Data**: Real-time APYs, TVL, utilization rates, prices for all markets
    - Direct contract queries for on-chain accuracy
    - API-based queries for comprehensive market data (more stable, includes historical data and mining rewards)
- **Account Data**: Full position analysis with API support
    - Contract-based: Health factor, collateral, borrow positions
    - API-based: Enhanced data with mining rewards, historical trends, risk metrics
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
- **JST Voting / Governance**: View proposals, cast votes, deposit/withdraw JST for voting power, reclaim votes
- **Energy Rental**: Rent energy from JustLend, calculate rental prices, query rental orders, return/cancel rentals
- **sTRX Staking**: Stake TRX to receive sTRX, unstake sTRX, claim staking rewards, check withdrawal eligibility

**General TRON Chain**

- **Balances**: TRX balance (with Sun/TRX conversion), TRC20/TRC1155 token balances
- **Blocks**: Latest block, block by number/hash, block number, chain ID
- **Transactions**: Fetch transaction details, receipts, wait for confirmation
- **Contracts**: Read/write any contract, fetch on-chain ABI, multicall (v2 & v3), deploy, estimate energy
- **Token Metadata**: TRC20 info (name/symbol/decimals/supply), TRC721 metadata, TRC1155 URI
- **Transfers**: Send TRX, transfer TRC20 tokens, approve spenders
- **Staking (Stake 2.0)**: Freeze/unfreeze TRX for BANDWIDTH or ENERGY, withdraw expired unfreeze
- **Address Utilities**: Hex ↔ Base58 conversion, address validation, resolution
- **Wallet**: Encrypted local wallet management via agent-wallet, multi-wallet support, sign messages, sign typed data (EIP-712)

## Supported Markets

| jToken | Underlying | Description |
|--------|-----------|-------------|
| jTRX   | TRX       | Native TRON token |
| jUSDT  | USDT      | Tether USD |
| jUSDC  | USDC      | USD Coin |
| jBTC   | BTC       | Bitcoin (wrapped) |
| jETH   | ETH       | Ethereum (wrapped) |
| jSUN   | SUN       | SUN token |
| jWIN   | WIN       | WINkLink |
| jTUSD  | TUSD      | TrueUSD |

## Prerequisites

- [Node.js](https://nodejs.org/) 20.0.0 or higher
- Optional: [TronGrid API key](https://www.trongrid.io/) for reliable mainnet access (strongly recommended)

## Installation

```bash
git clone https://github.com/justlend/mcp-server-justlend.git
cd mcp-server-justlend
npm install
```

## Configuration

### Wallet Setup (v1.0.2+)

Starting from v1.0.2, private keys are managed by [`@bankofai/agent-wallet`](https://www.npmjs.com/package/@bankofai/agent-wallet) — an encrypted local wallet solution. Private keys are **never** stored in environment variables, config files, or passed as function parameters. They are encrypted at rest in `~/.agent-wallet/` with proper file permissions (`0600`).

#### Zero-Config Auto-Generation

Simply start the server — if no wallet exists, one is automatically generated:

```bash
npm start
# → Wallet: auto-generated new wallet "default"
# → Address: TXxx...xxx
# → Encrypted private key stored in ~/.agent-wallet/
```

The wallet persists across restarts (the address does not change).

#### Import an Existing Wallet

To use an existing private key, import it via the `agent-wallet` CLI (recommended over MCP tool to avoid key exposure in conversation logs):

```bash
npx agent-wallet import <wallet-name> --private-key <hex>
npx agent-wallet import <wallet-name> --mnemonic "word1 word2 ... word12"
```

#### Multi-Wallet Management

```bash
# List all wallets
npx agent-wallet list

# Set active wallet
npx agent-wallet use <wallet-name>
```

You can also manage wallets at runtime via the MCP tools `list_wallets`, `set_active_wallet`, and `import_wallet`.

### Environment Variables

```bash
# Strongly recommended — avoids TronGrid 429 rate limiting on mainnet
export TRONGRID_API_KEY="your_trongrid_api_key"

# Optional: HTTP/SSE transport mode
export MCP_TRANSPORT="http"       # Use HTTP/SSE instead of stdio
export MCP_HTTP_PORT="3000"       # HTTP server port (default: 3000)
export MCP_HTTP_HOST="127.0.0.1"  # HTTP server host (default: 127.0.0.1)
```

### Client Configuration

#### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-server-justlend": {
      "type": "stdio",
      "command": "npx",
      "args": ["tsx", "@justlend/mcp-server-justlend"],
      "env": {
        "TRONGRID_API_KEY": "SET_VIA_SYSTEM_ENV"
      }
    }
  }
}
```

!!! tip
    No `TRON_PRIVATE_KEY` needed — the server uses the encrypted agent-wallet automatically.

#### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "mcp-server-justlend": {
      "type": "stdio",
      "command": "npx",
      "args": ["tsx", "@justlend/mcp-server-justlend"],
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

### Tools (54 total)

#### Wallet & Network

| Tool | Description | Write? |
|------|-------------|--------|
| `get_wallet_address` | Show active wallet address | No |
| `list_wallets` | List all wallets managed by agent-wallet | No |
| `set_active_wallet` | Switch the active wallet by name | No |
| `import_wallet` | Import a wallet from private key or mnemonic (CLI import recommended for security) | **Yes** |
| `get_supported_networks` | List available networks | No |
| `get_supported_markets` | List all jToken markets with addresses | No |

#### Market Data

| Tool | Description | Write? |
|------|-------------|--------|
| `get_market_data` | Detailed data for one market (APY, TVL, rates) - Contract query | No |
| `get_all_markets` | Overview of all markets - Contract query | No |
| `get_protocol_summary` | Comptroller config & protocol parameters - Contract query | No |
| `get_markets_from_api` | **[API]** All market data with mining rewards & trends | No |
| `get_dashboard_from_api` | **[API]** Protocol-level statistics (TVL, users, etc.) | No |
| `get_jtoken_details_from_api` | **[API]** Detailed jToken info with interest rate model | No |

#### Account & Balances

| Tool | Description | Write? |
|------|-------------|--------|
| `get_account_summary` | Full position: supplies, borrows, health factor - Contract query | No |
| `get_account_data_from_api` | **[API]** Enhanced account data with mining rewards & trends | No |
| `check_allowance` | Check TRC20 approval for jToken | No |
| `get_trx_balance` | TRX balance | No |
| `get_token_balance` | TRC20 token balance | No |

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

### Prompts (AI-Guided Workflows)

| Prompt | Description |
|--------|-------------|
| `supply_assets` | Step-by-step supply with balance checks and approval |
| `borrow_assets` | Safe borrowing with risk assessment and health factor checks |
| `repay_borrow` | Guided repayment with verification |
| `analyze_portfolio` | Comprehensive portfolio analysis with risk scoring |
| `compare_markets` | Find best supply/borrow opportunities |
| `rent_energy` | Guided energy rental with price estimation and balance checks |
| `stake_trx` | Guided TRX staking to sTRX with APY info and verification |

## Security Considerations

- **Encrypted wallet**: Private keys are encrypted at rest in `~/.agent-wallet/` with file permissions `0600`/`0700` — never stored in environment variables or config files
- **No key in parameters**: All signing functions use the agent-wallet internally; private keys are never passed as function parameters or exposed via MCP tools
- **Import via CLI**: Use `npx agent-wallet import` from a terminal rather than the `import_wallet` MCP tool to avoid key exposure in AI conversation logs
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
→ AI calls `calculate_energy_rental_price` with energyAmount=300000, durationDays=7, returns cost breakdown

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
