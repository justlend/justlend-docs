---
title: Deployed Contracts (Mainnet + Nile)
description: Base58 addresses for every JustLend DAO contract on TRON Mainnet, plus the Nile testnet subset. For machine consumers, the same data is available with Base58 / 0x / 41-hex formats in /developers/contracts.json.
---

# Deployed Contracts

!!! tip "Machine-readable contract directory"
    For agents and tooling that need every address in **TRON Base58 + EVM 0x-Hex + TRON-internal 41-Hex** form, download [`contracts.json`](contracts.json). The file is structured as `networks.{mainnet,nile}.{comptroller,governance,price_oracle,jtokens,interest_rate_models,strx}`, with each address record carrying `base58 / hex_evm / hex_tron / tronscan` fields. The tables below show **Base58 only** for readability; use the JSON for cross-chain bridges, EVM-side tooling, Etherscan-like indexers, and TronGrid calls that require `41`-prefixed hex.

!!! tip "Machine-readable ABIs"
    Every contract referenced on this page has a downloadable JSON ABI under [`abis/`](abis/jtoken.json):
    
    | Contract | ABI |
    |---|---|
    | jToken (CErc20) — `mint` / `borrow` / `repayBorrow` / `redeem` / `liquidateBorrow` | [`abis/jtoken.json`](abis/jtoken.json) |
    | jToken — TRX-specific `mint()` payable | [`abis/jtrx-mint.json`](abis/jtrx-mint.json) |
    | jToken — TRX-specific `repayBorrow()` payable | [`abis/jtrx-repay.json`](abis/jtrx-repay.json) |
    | Comptroller / Unitroller | [`abis/comptroller.json`](abis/comptroller.json) |
    | PriceOracle | [`abis/price-oracle.json`](abis/price-oracle.json) |
    | TRC20 (generic) | [`abis/trc20.json`](abis/trc20.json) |
    | GovernorAlpha / Bravo | [`abis/governor-alpha.json`](abis/governor-alpha.json) |
    | WJST (voting wrapper) | [`abis/wjst.json`](abis/wjst.json) |
    | Poly helper | [`abis/poly.json`](abis/poly.json) |
    | EnergyRental market | [`abis/energy-market.json`](abis/energy-market.json) |
    | EnergyRateModel | [`abis/energy-rate-model.json`](abis/energy-rate-model.json) |
    | sTRX | [`abis/strx.json`](abis/strx.json) |
    | InterestRateModel (jump-rate / whitepaper) | [`abis/interest-rate-model.json`](abis/interest-rate-model.json) |
    
    These are sourced from the same definitions the [JustLend MCP server](../ai_support/mcp_server.md) uses at runtime — see [`src/core/abis.ts`](https://github.com/justlend/mcp-server-justlend/blob/main/src/core/abis.ts) for the upstream TypeScript form.

!!! info "Network: TRON Mainnet (unless noted)"
    Everything in the main tables below is deployed on **TRON Mainnet** (Chain ID `0x2b6653dc`). For **Nile testnet** addresses see the [Nile Testnet](#nile-testnet) section at the bottom of this page or the `nile` block of `contracts.json`.

!!! warning "Decimals / precision"
    The JustLend DAO architecture treats every token amount in **its underlying's smallest unit**. Always read `decimals()` on the underlying TRC20 before constructing `mint`, `borrow`, `repayBorrow`, or `redeemUnderlying` amounts. Common cases: TRX/USDT/USDC = 6, USDD/ETH = 18, BTC/WBTC = 8. jToken amounts (`redeem`, `transfer`) use **8 decimals** regardless of the underlying. For the full enumeration and the units rationale, see [Glossary → jToken decimals](../resources/glossary.md#jtoken-decimals) and [Common Pitfalls #5](common_pitfalls.md#5-jtoken-8-underlying-varies-decimals).

## Address formats

TRON addresses appear in three equivalent formats. Human-facing tables on this page use Base58; machine consumers should use [`contracts.json`](contracts.json) for all three forms.

| Format | Example for Unitroller | Use cases |
|--------|-------------------------|-----------|
| Base58 | `TGjYzgCyPobsNS9n6WcbdLVR9dH7mWqFx7` | Wallets, Tronscan, TronWeb display, user prompts |
| EVM 0x-Hex | `0x4a33bf2666f2e75f3d6ad3b9ad316685d5c668d4` | EVM-side tooling, bridges, indexers, byte-address comparisons |
| TRON 41-Hex | `0x414a33bf2666f2e75f3d6ad3b9ad316685d5c668d4` | TronGrid / TronWeb low-level APIs that expect TRON-internal hex |

---

## Supply and Borrow Market — Core

| Component | Contract | Address | Tronscan |
|-----------|----------|---------|----------|
| Comptroller (proxy) | `Unitroller` | `TGjYzgCyPobsNS9n6WcbdLVR9dH7mWqFx7` | [Contract](https://tronscan.org/#/contract/TGjYzgCyPobsNS9n6WcbdLVR9dH7mWqFx7) |
| Comptroller (impl) | `Comptroller` | `TB23wYojvAsSx6gR8ebHiBqwSeABiBMPAr` | [Contract](https://tronscan.org/#/contract/TB23wYojvAsSx6gR8ebHiBqwSeABiBMPAr) |

The entrypoint that users and contracts call is **Unitroller** (the proxy). The implementation address rotates with upgrades.

## Supply and Borrow Market — jToken Markets

The address users interact with for `mint`/`borrow`/`repayBorrow`/`redeem`/`liquidateBorrow` is the **CErc20Delegator** (proxy). The **CErc20Delegate** address is the implementation behind it.

!!! warning "Legacy markets (marked `(legacy)`) — policy + support window"
    Rows tagged `(legacy)` — `jUSDCOLD`, `jUSDDOLD`, `jBUSDOLD`, `jSUNOLD`, `jUSDJ`, `jWBTT` — have been **closed to new supply and borrow** at the dApp / policy layer.

    **What still works on a legacy market:**

    - Read-only queries against the contract (`balanceOf`, `borrowBalanceCurrent`, `exchangeRateCurrent`, etc.) — unchanged forever.
    - Unwinding existing positions: `repayBorrow`, `redeem`, `redeemUnderlying`, `liquidateBorrow`.
    - The underlying TRC20 of the legacy market is unaffected — only the JustLend market is frozen.

    **What does NOT work:**

    - The dApp UI suppresses these markets from the supply / borrow lists.
    - New deposits are operationally discouraged; programmatic callers SHOULD filter `status == "active"` from [`contracts.json`](contracts.json) and avoid routing new flow to legacy markets even though a `mint()` call would technically succeed at the contract level.

    **Support window.** There is **no announced sunset date** for legacy contracts. They remain live and queryable indefinitely. Addresses are never reused; the same delegator address always refers to the same market. JustLend has not committed to a deprecation timeline — treat "legacy" as "supply/borrow frozen, read forever."

    For the most up-to-date status table, see [`apis.md §2`](apis.md#2-jtoken-address-reference) or filter [`contracts.json`](contracts.json) by `status`.

!!! note "ETH / ETHB display-name swap"
    The JustLend dApp UI labels two markets with renamed legends:
    
    * The market with delegator `TR7BUFRQeq1w5jAZf1FKx85SHuX6PfMqsV` (this doc's `jETH` row) is now displayed in the dApp as **"ETH"** (formerly "ETHOLD"). Underlying TRC20: `THb4CqiFdwNHsWsQCs4JhzwjMWys4aqCbF`.
    * The market with delegator `TWBxQMb6RD3qmkXUXpNwVCYbL8SHNreru6` (this doc's `jETHB` row) is now displayed in the dApp as **"ETHB"** (formerly "ETH"). Underlying TRC20: `TRFe3hT5oYhjSZ6f3ji5FJ7YCfrkWnHRvh`.
    
    The on-chain addresses are unchanged — only the dApp display names swapped.

## Supply and Borrow Market V1

| Market | Underlying TRC20 | CErc20Delegator (entrypoint) | CErc20Delegate (impl) |
|--------|------------------|------------------------------|------------------------|
| jTRX | _native_ | [`TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP`](https://tronscan.org/#/token20/TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP) | NA |
| jUSDT | [`TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t`](https://tronscan.org/#/token20/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t) | [`TXJgMdjVX5dKiQaUi9QobwNxtSQaFqccvd`](https://tronscan.org/#/contract/TXJgMdjVX5dKiQaUi9QobwNxtSQaFqccvd) | [`TLjn59xNM7VEK6VZ3VQ8Y1ipxsdsFka5wZ`](https://tronscan.org/#/contract/TLjn59xNM7VEK6VZ3VQ8Y1ipxsdsFka5wZ) |
| jUSDD | [`TXDk8mbtRbXeYuMNS83CfKPaYYT8XWv9Hz`](https://tronscan.org/#/token20/TXDk8mbtRbXeYuMNS83CfKPaYYT8XWv9Hz) | [`TKFRELGGoRgiayhwJTNNLqCNjFoLBh3Mnf`](https://tronscan.org/#/token20/TKFRELGGoRgiayhwJTNNLqCNjFoLBh3Mnf) | [`TLrEfG4QCbax8MTYgZzmjj4gE8RPVNvUn4`](https://tronscan.org/#/token20/TLrEfG4QCbax8MTYgZzmjj4gE8RPVNvUn4) |
| jUSDCOLD (legacy) | [`TLZSucJRjnqBKwvQz6n5hd29gbS4P7u7w8`](https://tronscan.org/#/token20/TLZSucJRjnqBKwvQz6n5hd29gbS4P7u7w8) | [`TNSBA6KvSvMoTqQcEgpVK7VhHT3z7wifxy`](https://tronscan.org/#/contract/TNSBA6KvSvMoTqQcEgpVK7VhHT3z7wifxy) | [`THQY8YX19jLFSFg1xhthM5wb7xZvKLCzgq`](https://tronscan.org/#/contract/THQY8YX19jLFSFg1xhthM5wb7xZvKLCzgq) |
| jUSDJ (legacy) | [`TMwFHYXLJaRUPeW6421aqXL4ZEzPRFGkGT`](https://tronscan.org/#/token20/TMwFHYXLJaRUPeW6421aqXL4ZEzPRFGkGT) | [`TL5x9MtSnDy537FXKx53yAaHRRNdg9TkkA`](https://tronscan.org/#/contract/TL5x9MtSnDy537FXKx53yAaHRRNdg9TkkA) | [`TYSHTEq9NFSgst94saeRvt6rAYgWkqMFbj`](https://tronscan.org/#/contract/TYSHTEq9NFSgst94saeRvt6rAYgWkqMFbj) |
| jTUSD | [`TUpMhErZL2fhh4sVNULAbNKLokS4GjC1F4`](https://tronscan.org/#/token20/TUpMhErZL2fhh4sVNULAbNKLokS4GjC1F4) | [`TSXv71Fy5XdL3Rh2QfBoUu3NAaM4sMif8R`](https://tronscan.org/#/contract/TSXv71Fy5XdL3Rh2QfBoUu3NAaM4sMif8R) | [`THbrSjDsDA2KJRxx8K73tN7vLgaXSUNQFk`](https://tronscan.org/#/contract/THbrSjDsDA2KJRxx8K73tN7vLgaXSUNQFk) |
| jUSD1 | [`TPFqcBAaaUMCSVRCqPaQ9QnzKhmuoLR6Rc`](https://tronscan.org/#/token20/TPFqcBAaaUMCSVRCqPaQ9QnzKhmuoLR6Rc) | [`TBEKggwqFkrc4KckQVR9BLucAmQugafEZf`](https://tronscan.org/#/token20/TBEKggwqFkrc4KckQVR9BLucAmQugafEZf) | [`TRo2exz6ZHn6W3Ey3G93FnzhWvjLPUcR2B`](https://tronscan.org/#/contract/TRo2exz6ZHn6W3Ey3G93FnzhWvjLPUcR2B) |
| jwstUSDT | [`TGkxzkDKyMeq2T7edKnyjZoFypyzjkkssq`](https://tronscan.org/#/token20/TGkxzkDKyMeq2T7edKnyjZoFypyzjkkssq) | [`TD5SdLw5scR6mXgyMK2xKrFJpauDjpKqrW`](https://tronscan.org/#/token20/TD5SdLw5scR6mXgyMK2xKrFJpauDjpKqrW) | [`TUx4cV8FQNR5W4FhtF7mHZwaJMoco2464o`](https://tronscan.org/#/token20/TUx4cV8FQNR5W4FhtF7mHZwaJMoco2464o) |
| jsTRX | [`TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5`](https://tronscan.org/#/token20/TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5) | [`TJQ9rbVe9ei3nNtyGgBL22Fuu2xYjZaLAQ`](https://tronscan.org/#/token20/TJQ9rbVe9ei3nNtyGgBL22Fuu2xYjZaLAQ) | [`TCyNbCipGbAybb8rG4aatEoEnfuYpVYCPP`](https://tronscan.org/#/token20/TCyNbCipGbAybb8rG4aatEoEnfuYpVYCPP) |
| jSUN | [`TSSMHYeV2uE9qYH95DqyoCuNCzEL1NvU3S`](https://tronscan.org/#/token20/TSSMHYeV2uE9qYH95DqyoCuNCzEL1NvU3S) | [`TPXDpkg9e3eZzxqxAUyke9S4z4pGJBJw9e`](https://tronscan.org/#/contract/TPXDpkg9e3eZzxqxAUyke9S4z4pGJBJw9e) | [`TM82erAZJSP7NKc17JdTnzVC8WKJHismWB`](https://tronscan.org/#/contract/TM82erAZJSP7NKc17JdTnzVC8WKJHismWB) |
| jBTT | [`TAFjULxiVgT4qWk6UZwjqwZXTSaGaqnVp4`](https://tronscan.org/#/token20/TAFjULxiVgT4qWk6UZwjqwZXTSaGaqnVp4) | [`TUaUHU9Dy8x5yNi1pKnFYqHWojot61Jfto`](https://tronscan.org/#/token20/TUaUHU9Dy8x5yNi1pKnFYqHWojot61Jfto) | [`TH3x5EqLnPduHNX41MaCCb2UfnfFMLuYwe`](https://tronscan.org/#/token20/TH3x5EqLnPduHNX41MaCCb2UfnfFMLuYwe) |
| jNFT | [`TFczxzPhnThNSqr5by8tvxsdCFRRz6cPNq`](https://tronscan.org/#/token20/TFczxzPhnThNSqr5by8tvxsdCFRRz6cPNq) | [`TFpPyDCKvNFgos3g3WVsAqMrdqhB81JXHE`](https://tronscan.org/#/contract/TFpPyDCKvNFgos3g3WVsAqMrdqhB81JXHE) | [`TLkUdtDBLMfJdXni2iTa4u2DKM53XmDJHi`](https://tronscan.org/#/contract/TLkUdtDBLMfJdXni2iTa4u2DKM53XmDJHi) |
| jJST | [`TCFLL5dx5ZJdKnWuesXxi1VPwjLVmWZZy9`](https://tronscan.org/#/token20/TCFLL5dx5ZJdKnWuesXxi1VPwjLVmWZZy9) | [`TWQhCXaWz4eHK4Kd1ErSDHjMFPoPc9czts`](https://tronscan.org/#/contract/TWQhCXaWz4eHK4Kd1ErSDHjMFPoPc9czts) | [`TQ2sbnmxtR7jrNk4nxz2A8f9sneCqmk6SB`](https://tronscan.org/#/contract/TQ2sbnmxtR7jrNk4nxz2A8f9sneCqmk6SB) |
| jWIN | [`TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7`](https://tronscan.org/#/token20/TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7) | [`TRg6MnpsFXc82ymUPgf5qbj59ibxiEDWvv`](https://tronscan.org/#/contract/TRg6MnpsFXc82ymUPgf5qbj59ibxiEDWvv) | [`TW3GyD3hYkKwzSGytWwWGXpe2a93zCpRzJ`](https://tronscan.org/#/contract/TW3GyD3hYkKwzSGytWwWGXpe2a93zCpRzJ) |
| jHTX | [`TUPM7K8REVzD2UdV4R5fe5M8XbnR2DdoJ6`](https://tronscan.org/#/token20/TUPM7K8REVzD2UdV4R5fe5M8XbnR2DdoJ6) | [`TDA1mWPyAjTRATMGA55UTswGAHhV2itEXR`](https://tronscan.org/#/contract/TDA1mWPyAjTRATMGA55UTswGAHhV2itEXR) | [`TJD7nb5Wq1P1rRi3Se2vLpLhksALdW8adb`](https://tronscan.org/#/contract/TJD7nb5Wq1P1rRi3Se2vLpLhksALdW8adb) |
| jBTC | [`TN3W4H6rK2ce4vX9YnFQHwKENnHjoxb3m9`](https://tronscan.org/#/token20/TN3W4H6rK2ce4vX9YnFQHwKENnHjoxb3m9) | [`TLeEu311Cbw63BcmMHDgDLu7fnk9fqGcqT`](https://tronscan.org/#/contract/TLeEu311Cbw63BcmMHDgDLu7fnk9fqGcqT) | [`TVsKSRgRoMcCp798qqRGesXRfzy2MzRjkR`](https://tronscan.org/#/contract/TVsKSRgRoMcCp798qqRGesXRfzy2MzRjkR) |
| jWBTC | [`TYhWwKpw43ENFWBTGpzLHn3882f2au7SMi`](https://tronscan.org/#/token20/TYhWwKpw43ENFWBTGpzLHn3882f2au7SMi) | [`TVyvpmaVmz25z2GaXBDDjzLZi5iR5dBzGd`](https://tronscan.org/#/token20/TVyvpmaVmz25z2GaXBDDjzLZi5iR5dBzGd) | [`TDwUJqxB1962DSfKHWMnEu1sWMGGRvHDB5`](https://tronscan.org/#/contract/TDwUJqxB1962DSfKHWMnEu1sWMGGRvHDB5) |
| jETHB | [`TRFe3hT5oYhjSZ6f3ji5FJ7YCfrkWnHRvh`](https://tronscan.org/#/token20/TRFe3hT5oYhjSZ6f3ji5FJ7YCfrkWnHRvh) | [`TWBxQMb6RD3qmkXUXpNwVCYbL8SHNreru6`](https://tronscan.org/#/token20/TWBxQMb6RD3qmkXUXpNwVCYbL8SHNreru6) | [`TS9fVh58y2RMDnpucGXkbfZhAJxmGafGqe`](https://tronscan.org/#/token20/TS9fVh58y2RMDnpucGXkbfZhAJxmGafGqe) |
| jETH | [`THb4CqiFdwNHsWsQCs4JhzwjMWys4aqCbF`](https://tronscan.org/#/token20/THb4CqiFdwNHsWsQCs4JhzwjMWys4aqCbF) | [`TR7BUFRQeq1w5jAZf1FKx85SHuX6PfMqsV`](https://tronscan.org/#/token20/TR7BUFRQeq1w5jAZf1FKx85SHuX6PfMqsV) | [`TQBvTVisiceDvsQVbLbcYyWQGWP7wtaQnc`](https://tronscan.org/#/contract/TQBvTVisiceDvsQVbLbcYyWQGWP7wtaQnc) |
| jWBTT (legacy) | [`TKfjV9RNKJJCqPvBtK8L7Knykh7DNWvnYt`](https://tronscan.org/#/token20/TKfjV9RNKJJCqPvBtK8L7Knykh7DNWvnYt) | [`TUY54PVeH6WCcYCd6ZXXoBDsHytN9V5PXt`](https://tronscan.org/#/contract/TUY54PVeH6WCcYCd6ZXXoBDsHytN9V5PXt) | [`TV4WWBqBfn1kd4KmpYeSJpVAfybfrxEN9L`](https://tronscan.org/#/contract/TV4WWBqBfn1kd4KmpYeSJpVAfybfrxEN9L) |
| jBUSDOLD (legacy) | [`TMz2SWatiAtZVVcH2ebpsbVtYwUPT9EdjH`](https://tronscan.org/#/token20/TMz2SWatiAtZVVcH2ebpsbVtYwUPT9EdjH) | [`TLHASseQymmpGQdfAyNjkMXFTJh8nzR2x2`](https://tronscan.org/#/contract/TLHASseQymmpGQdfAyNjkMXFTJh8nzR2x2) | [`TNRUqbYfYv4iizWa1b2kd6ZBaoh5zrg3yk`](https://tronscan.org/#/contract/TNRUqbYfYv4iizWa1b2kd6ZBaoh5zrg3yk) |
| jUSDDOLD (legacy) | [`TPYmHEhy5n8TCEfYGqW2rPxsghSfzghPDn`](https://tronscan.org/#/token20/TPYmHEhy5n8TCEfYGqW2rPxsghSfzghPDn) | [`TX7kybeP6UwTBRHLNPYmswFESHfyjm9bAS`](https://tronscan.org/#/contract/TX7kybeP6UwTBRHLNPYmswFESHfyjm9bAS) | [`TFdTqrMyb6PMMqTa9vnhmQHDFDU2oUhw9W`](https://tronscan.org/#/contract/TFdTqrMyb6PMMqTa9vnhmQHDFDU2oUhw9W) |
| jSUNOLD (legacy) | [`TKkeiboTkxXKJpbmVFbv4a8ov5rAfRDMf9`](https://tronscan.org/#/token20/TKkeiboTkxXKJpbmVFbv4a8ov5rAfRDMf9) | [`TGBr8uh9jBVHJhhkwSJvQN2ZAKzVkxDmno`](https://tronscan.org/#/contract/TGBr8uh9jBVHJhhkwSJvQN2ZAKzVkxDmno) | [`TSCpzKvJfXHj1HW5jKg9dZA8z9aMxxGLd8`](https://tronscan.org/#/contract/TSCpzKvJfXHj1HW5jKg9dZA8z9aMxxGLd8) |

### Interest Rate Models

| Model | Type | Address | Tronscan |
|-------|------|---------|----------|
| WhitePaperModelTRX | `WhitePaperInterestRateModel` | `TF8B4iysAGfrssdQhMJGYsdd9SZoxGsH7M` | [Contract](https://tronscan.org/#/contract/TF8B4iysAGfrssdQhMJGYsdd9SZoxGsH7M) |
| WhitePaperModelBTC | `WhitePaperInterestRateModel` | `TYJi9q4qLQWoBiKmMQY3Mn81tmhw7SeCmh` | [Contract](https://tronscan.org/#/contract/TYJi9q4qLQWoBiKmMQY3Mn81tmhw7SeCmh) |
| jumpRateTRX | `JumpRateModelV2` | `TMca13trZmVvVttrGWJyUSm33qZdohDDuh` | [Contract](https://tronscan.org/#/contract/TMca13trZmVvVttrGWJyUSm33qZdohDDuh) |
| jumpRateUSDDOLD | `JumpRateModelV2` | `TDoB7y9HHj6bXTwEe6BhfAkdETjQR2He6u` | [Contract](https://tronscan.org/#/contract/TDoB7y9HHj6bXTwEe6BhfAkdETjQR2He6u) |
| jumpRateUSDT | `JumpRateModelV2` | `TTetZxp98wcPaciyBMHYvQkS735RZ3tyXY` | [Contract](https://tronscan.org/#/contract/TTetZxp98wcPaciyBMHYvQkS735RZ3tyXY) |
| jumpRatewstUSDT | `JumpRateModelV2` | `TPqKsaTnSKEU3aGHanpVFNU3cE8SmJsAYz` | [Contract](https://tronscan.org/#/contract/TPqKsaTnSKEU3aGHanpVFNU3cE8SmJsAYz) |
| jumpRatesTRX | `JumpRateModelV2` | `TW4fpkc98kzVbdiPhutCg2uivwVJ9MDa2P` | [Contract](https://tronscan.org/#/contract/TW4fpkc98kzVbdiPhutCg2uivwVJ9MDa2P) |
| jumpRateSUN | `JumpRateModelV2` | `THCVC3DHgZ5qmUcJPutw7TrMMfj1h2bvkZ` | [Contract](https://tronscan.org/#/contract/THCVC3DHgZ5qmUcJPutw7TrMMfj1h2bvkZ) |
| jumpRateBTT | `JumpRateModelV2` | `TQ9zMkrqgej7GjLdMrpNuURozg8J2fSXsW` | [Contract](https://tronscan.org/#/contract/TQ9zMkrqgej7GjLdMrpNuURozg8J2fSXsW) |
| jumpRateNFT | `JumpRateModelV2` | `TBE9tkWYdZPEHLNeKC6Xn44YFLpieiM3xq` | [Contract](https://tronscan.org/#/contract/TBE9tkWYdZPEHLNeKC6Xn44YFLpieiM3xq) |
| jumpRateJST | `JumpRateModelV2` | `TMNXjQTa8x4wNHBa3X647KRnkRQpSuXBRT` | [Contract](https://tronscan.org/#/contract/TMNXjQTa8x4wNHBa3X647KRnkRQpSuXBRT) |
| jumpRateWIN | `JumpRateModelV2` | `TBtChPo34CGJkb1QVEwPhxS8HQE2Xp7ir2` | [Contract](https://tronscan.org/#/contract/TBtChPo34CGJkb1QVEwPhxS8HQE2Xp7ir2) |
| jumpRateUSDJ | `JumpRateModelV2` | `TLScd7kpWnKADtH7ZXKzrJHAxJUnjiiExq` | [Contract](https://tronscan.org/#/contract/TLScd7kpWnKADtH7ZXKzrJHAxJUnjiiExq) |
| jumpRateUSDC | `JumpRateModelV2` | `TDECE4PZFEkmTyFk9sJMya9PY99BapHpyP` | [Contract](https://tronscan.org/#/contract/TDECE4PZFEkmTyFk9sJMya9PY99BapHpyP) |
| jumpRateTUSD | `JumpRateModelV2` | `TLY3wRNGrQpJCZrYKu9VjntMj2kNxisAL2` | [Contract](https://tronscan.org/#/contract/TLY3wRNGrQpJCZrYKu9VjntMj2kNxisAL2) |
| jumpRateBTC | `JumpRateModelV2` | `TYJi9q4qLQWoBiKmMQY3Mn81tmhw7SeCmh` | [Contract](https://tronscan.org/#/contract/TYJi9q4qLQWoBiKmMQY3Mn81tmhw7SeCmh) |
| jumpRateETHB | `JumpRateModelV2` | `TD5wmR7NfBM2JdSGSTTq1MgMARX2k5KE2b` | [Contract](https://tronscan.org/#/contract/TD5wmR7NfBM2JdSGSTTq1MgMARX2k5KE2b) |
| jumpRateWBTT | `JumpRateModelV2` | `TJAfCJdJZa44pG5adQGLMLh27hJqPeLxod` | [Contract](https://tronscan.org/#/contract/TJAfCJdJZa44pG5adQGLMLh27hJqPeLxod) |
| jumpRateBUSD | `JumpRateModelV2` | `TUSGt1WAYeJSV94M5muFi2KvtE6EquZPUC` | [Contract](https://tronscan.org/#/contract/TUSGt1WAYeJSV94M5muFi2KvtE6EquZPUC) |
| jumpRateSUNOLD | `JumpRateModelV2` | `TK7WVRz34wUVRCpsgbW1wUCPmh5bSnCqg1` | [Contract](https://tronscan.org/#/contract/TK7WVRz34wUVRCpsgbW1wUCPmh5bSnCqg1) |
| jumpRateETH | `JumpRateModelV2` | `TCiKn6EFBsNrNCFQXWaEuAxr8Su3y4Rx9D` | [Contract](https://tronscan.org/#/contract/TCiKn6EFBsNrNCFQXWaEuAxr8Su3y4Rx9D) |
| jumpRateUSD1 | `JumpRateModelV2` | `TKgX5vEds8UW8bd5fSDGHpTT4UwmVz4yPS` | [Contract](https://tronscan.org/#/contract/TKgX5vEds8UW8bd5fSDGHpTT4UwmVz4yPS) |

See [Interest Rate Model](supply_and_borrow_market/interest_rate_model.md) for the formulas backing these contracts.

### Price Oracle

| Component | Contract | Address | Tronscan |
|-----------|----------|---------|----------|
| Oracle Proxy | `PriceOracleProxy` | `TGnYnSn4G9PgWFj7QQemh4YMZKp3fkympJ` | [Contract](https://tronscan.org/contract/TGnYnSn4G9PgWFj7QQemh4YMZKp3fkympJ/code) |
| Oracle (impl) | `PriceOracle` | `TMiNCmvD3zdsv6mk7niBU6NPBzVNjYMQTV` | [Contract](https://tronscan.org/#/contract/TMiNCmvD3zdsv6mk7niBU6NPBzVNjYMQTV/code) |

Prices are denominated in **TRX** , scaled by `1e^(33 - tokenDecimal)`. See [Price Oracle](supply_and_borrow_market/price_oracle.md).


### Governance

| Component | Contract | Address | Tronscan |
|-----------|----------|---------|----------|
| Governor Proxy | `GovernorBravoDelegator` | `TEqiF5JbhDPD77yjEfnEMncGRZNDt2uogD` | [Contract](https://tronscan.org/#/contract/TEqiF5JbhDPD77yjEfnEMncGRZNDt2uogD) |
| Governor (impl) | `GovernorBravoDelegate` | `TCiQTkxhzwSeXhRsNdHCvrxHRAvpjQn5Dt` | [Contract](https://tronscan.org/#/contract/TCiQTkxhzwSeXhRsNdHCvrxHRAvpjQn5Dt) |
| Time-lock | `Timelock` | `TRWNvb15NmfNKNLhQpxefFz7cNjrYjEw7x` | [Contract](https://tronscan.org/#/contract/TRWNvb15NmfNKNLhQpxefFz7cNjrYjEw7x) |

See [Governance](supply_and_borrow_market/governance.md) for the proposal lifecycle and voting flow.

### Comptroller

| Component | Contract | Address | Tronscan |
|-----------|----------|---------|----------|
| Comptroller Proxy | `Unitroller` | `TGjYzgCyPobsNS9n6WcbdLVR9dH7mWqFx7` | [Contract](https://tronscan.org/contract/TGjYzgCyPobsNS9n6WcbdLVR9dH7mWqFx7/code) |
| Comptroller (impl) | `Comptroller` | `TB23wYojvAsSx6gR8ebHiBqwSeABiBMPAr` | [Contract](https://tronscan.org/contract/TB23wYojvAsSx6gR8ebHiBqwSeABiBMPAr/code) |

See [Comptroller](supply_and_borrow_market/comptroller.md) for Comptroller details.


## Supply and Borrow Market V2

### Moolah Market

| Component | Contract | Address | Tronscan |
| --- | --- | --- | --- |
| Market Entrypoint | `MoolahProxy` | `TDH4dhmVQQNc1ZNudJwWzBcs2h6ahhWrpp` | [Contract](https://tronscan.org/#/contract/TDH4dhmVQQNc1ZNudJwWzBcs2h6ahhWrpp) |
| Market Implementation | `Moolah` | `TKEiKtSaqUboeBmZxcSp8Z2CJUDGk4BT3a` | [Contract](https://tronscan.org/#/contract/TKEiKtSaqUboeBmZxcSp8Z2CJUDGk4BT3a) |

### Moolah Vault

| Component / Vault | Contract | Address | Tronscan |
| --- | --- | --- | --- |
| Vault Factory Proxy | `MoolahVaultFactoryProxy` | `TYoUEF2jB5WdTSVKRTmbUtC9iieVUPY1XK` | [Contract](https://tronscan.org/#/contract/TYoUEF2jB5WdTSVKRTmbUtC9iieVUPY1XK) |
| Vault Factory (impl) | `MoolahVaultFactory` | `TTt6eWpEPZPBE5HiCRsgrjFfAh21kmFRcT` | [Contract](https://tronscan.org/#/contract/TTt6eWpEPZPBE5HiCRsgrjFfAh21kmFRcT) |
| Vault Template | `MoolahVaultV1` | `TVE5y9aSf1f7CiRjPJM4MgYXgCqBoJGE9z` | [Contract](https://tronscan.org/#/contract/TVE5y9aSf1f7CiRjPJM4MgYXgCqBoJGE9z) |
| **USDT** Vault | `usdtVault` | `TXejU9jmd1ooQyY3Zmpo15yN7MjSFYUESg` | [Contract](https://tronscan.org/#/contract/TXejU9jmd1ooQyY3Zmpo15yN7MjSFYUESg) |
| **USDD** Vault | `usddVault` | `TA3q7XjdBQWb4qFxaPULUsnjvVZGgC9Brz` | [Contract](https://tronscan.org/#/contract/TA3q7XjdBQWb4qFxaPULUsnjvVZGgC9Brz) |
| **TRX** Vault | `trxVault` | `THpxp8RpCUGk55dV7oL1LfxDeP9QvouxmM` | [Contract](https://tronscan.org/#/contract/THpxp8RpCUGk55dV7oL1LfxDeP9QvouxmM) |

### TRX Provider

| Component | Contract | Address | Tronscan |
| --- | --- | --- | --- |
| TRX Provider Proxy | `TrxProviderProxy` | `TMDENHFSiRzmJNSEBAFmrDbLkQ672iPN8H` | [Contract](https://tronscan.org/#/contract/TMDENHFSiRzmJNSEBAFmrDbLkQ672iPN8H) |
| TRX Provider (impl) | `TrxProvider` | `TDsc5u5h9AjYfnH3zh92SH5dJouHSxiim2` | [Contract](https://tronscan.org/#/contract/TDsc5u5h9AjYfnH3zh92SH5dJouHSxiim2) |

### Interest Rate Model

| Model | Type | Address | Tronscan |
| --- | --- | --- | --- |
| IrmProxy | `IrmProxy` | `TSsuwbvUKAVgRmSghXT7i38PgHWpW12wQ1` | [Contract](https://tronscan.org/#/contract/TSsuwbvUKAVgRmSghXT7i38PgHWpW12wQ1) |
| InterestRateModel (impl) | `InterestRateModel` | `TM96c8n7FrF9rGVg6h4MatA1ghY6tjneWD` | [Contract](https://tronscan.org/#/contract/TM96c8n7FrF9rGVg6h4MatA1ghY6tjneWD) |

### Resilient Oracle

| Component / Asset | Contract | Address | Tronscan |
| --- | --- | --- | --- |
| Resilient Oracle Proxy | `ResilientOracleProxy` | `TUDXEUA6hNiWPm54cMifoxCZU28zRu6bPc` | [Contract](https://tronscan.org/#/contract/TUDXEUA6hNiWPm54cMifoxCZU28zRu6bPc) |
| Resilient Oracle (impl) | `ResilientOracl` | `TN6B7nsKYySF7sqD9xzZPiPmXyoX3ZpbGD` | [Contract](https://tronscan.org/#/contract/TN6B7nsKYySF7sqD9xzZPiPmXyoX3ZpbGD) |
| Bound Validator Proxy | `BoundValidatorProxy` | `TEfEgB5LjkQJXYhrKp4j14xUGLGD1NK4zC` | [Contract](https://tronscan.org/#/contract/TEfEgB5LjkQJXYhrKp4j14xUGLGD1NK4zC) |
| Bound Validator (impl) | `BoundValidator` | `TUQJWn72TV5NuAy7oCV95mRcJgrrFjxhdc` | [Contract](https://tronscan.org/#/contract/TUQJWn72TV5NuAy7oCV95mRcJgrrFjxhdc) |
| **USDD** Price Oracle | `UsddPriceOracle` | `TJt3mT8MrzxShunorzLbq3otzv1DK6Na34` | [Contract](https://tronscan.org/#/contract/TJt3mT8MrzxShunorzLbq3otzv1DK6Na34) |
| **USDT** Price Oracle | `UsdtPriceOracle` | `THj72uK3LdAXAGyE4fVuAWx7HwQy4RvEhb` | [Contract](https://tronscan.org/#/contract/THj72uK3LdAXAGyE4fVuAWx7HwQy4RvEhb) |
| **TRX** Price Oracle | `TrxPriceOracle` | `TMEGS6D356KWRSW3fDKmARpQS8AoXi5uCG` | [Contract](https://tronscan.org/#/contract/TMEGS6D356KWRSW3fDKmARpQS8AoXi5uCG) |
| **BTC** Price Oracle | `BtcPriceOracle` | `TBcM6vym7Y2PDuaeCY7hmCsY5V3DrXENaV` | [Contract](https://tronscan.org/#/contract/TBcM6vym7Y2PDuaeCY7hmCsY5V3DrXENaV) |
| **sTRX** Price Oracle | `StrxOracle` | `TYEeXbju2oC4NiBbSzMvwG59nS8QCsWZZg` | [Contract](https://tronscan.org/#/contract/TYEeXbju2oC4NiBbSzMvwG59nS8QCsWZZg) |
| **BTT** Price Oracle | `BttPriceOracle` | `TBByEevGPinzpVvF2dLK7WvXkE8qmrC3NH` | [Contract](https://tronscan.org/#/contract/TBByEevGPinzpVvF2dLK7WvXkE8qmrC3NH) |
| **ETH** Price Oracle | `EthPriceOracle` | `TAPioY4J4t9gRt31ioTZiHu3m5mLdH38w2` | [Contract](https://tronscan.org/#/contract/TAPioY4J4t9gRt31ioTZiHu3m5mLdH38w2) |
| **JST** Price Oracle | `JstPriceOracle` | `TQxH2UdxKizxbHTTgtmfJzgwKL1ToQ53B8` | [Contract](https://tronscan.org/#/contract/TQxH2UdxKizxbHTTgtmfJzgwKL1ToQ53B8) |
| **NFT** Price Oracle | `NftPriceOracle` | `TN9n41jPVfZcyEfHp69DmUsJtyy96QNRXc` | [Contract](https://tronscan.org/#/contract/TN9n41jPVfZcyEfHp69DmUsJtyy96QNRXc) |
| **SUN** Price Oracle | `SunPriceOracle` | `TTDb7ghCjH9n9x7kGvni6Gvdt4DLRNaQwr` | [Contract](https://tronscan.org/#/contract/TTDb7ghCjH9n9x7kGvni6Gvdt4DLRNaQwr) |
| **TUSD** Price Oracle | `TusdPriceOracle` | `TXnMhh4vLsP6HxvhviKH3Tkhr55fLS9h52` | [Contract](https://tronscan.org/#/contract/TXnMhh4vLsP6HxvhviKH3Tkhr55fLS9h52) |
| **USD1** Price Oracle | `Usd1PriceOracle` | `TQB7BcxFpqDTs9jC3ohBAf24ZGxGwrmSDg` | [Contract](https://tronscan.org/#/contract/TQB7BcxFpqDTs9jC3ohBAf24ZGxGwrmSDg) |
| **WIN** Price Oracle | `WinPriceOracle` | `TXE1wGnzMayc2QSkgycz1uu6fu2yUpPNbL` | [Contract](https://tronscan.org/#/contract/TXE1wGnzMayc2QSkgycz1uu6fu2yUpPNbL) |
| **wstUSDT** Price Oracle | `WstusdtOracle` | `TW3Yf5mshdR2uBDuQCoyW1rsaQdnoPppub` | [Contract](https://tronscan.org/#/contract/TW3Yf5mshdR2uBDuQCoyW1rsaQdnoPppub) |

### Liquidation

| Component | Contract | Address | Tronscan |
| --- | --- | --- | --- |
| Liquidator Proxy | `LiquidatorProxy` | `TKX8nUY8otA4d9qV1tDuN5BLSrxkr9pWa6` | [Contract](https://tronscan.org/#/contract/TKX8nUY8otA4d9qV1tDuN5BLSrxkr9pWa6) |
| Liquidator (impl) | `Liquidator` | `TJHdh4LG9eLiGq5qW7NnyczuFU48YUCyhh` | [Contract](https://tronscan.org/#/contract/TJHdh4LG9eLiGq5qW7NnyczuFU48YUCyhh) |
| Public Liquidator Proxy | `PublicLiquidatorProxy` | `TGDuQaHtvadVL5z9PMM874CaehQnwf3qJi` | [Contract](https://tronscan.org/#/contract/TGDuQaHtvadVL5z9PMM874CaehQnwf3qJi) |
| Public Liquidator (impl) | `PublicLiquidator` | `TUM8vMhR3MN5jmqYPxvwEV3erwJy374f6c` | [Contract](https://tronscan.org/#/contract/TUM8vMhR3MN5jmqYPxvwEV3erwJy374f6c) |
| Lending Fee Recipient Proxy | `LendingFeeRecipientProxy` | `TMzGb5Ma85oYMcnmVFjhvS1HYr6MRSspmE` | [Contract](https://tronscan.org/#/contract/TMzGb5Ma85oYMcnmVFjhvS1HYr6MRSspmE) |
| Lending Fee Recipient (impl) | `LendingFeeRecipient` | `TAqxyXczXXFpQQiycoSDVopgBCMDmgKrK2` | [Contract](https://tronscan.org/#/contract/TAqxyXczXXFpQQiycoSDVopgBCMDmgKrK2) |

See [SBMV2](supply_and_borrow_market/sbmV2.md) for more details.


## Staked TRX

| Component | Contract | Address | Tronscan |
|-----------|----------|---------|----------|
| StakedTRX | `sTRX` | `TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5` | [Token20](https://tronscan.org/#/token20/TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5) |

See [Staked TRX](staked_trx.md) for the contract reference.

## Energy Rental

| Component | Contract | Address | Tronscan |
|-----------|----------|---------|----------|
| EnergyRental | `EnergyRental` | `TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd` | [Contract](https://tronscan.org/#/contract/TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd) |

See [Energy Rental](energy_rental.md) for the contract reference.

---

## Nile Testnet

!!! warning "Testnet — not the production protocol"
    Use these addresses only for development and integration testing. Some Nile contracts are placeholder/stub addresses — when in doubt, call `get_supported_networks` / `get_supported_markets` on the [JustLend MCP server](../ai_support/mcp_server.md) for the live runtime view, or consult the [`chains.ts` Nile section](https://github.com/justlend/mcp-server-justlend/blob/main/src/core/chains.ts).

| Component | Contract | Address |
|-----------|----------|---------|
| Comptroller (proxy / entrypoint) | `Unitroller` | `TJUCStq3WqfKqZLuZje5v7z6Ua6iBry1P6` |
| Governance | `GovernorBravoDelegator` | `TYCNENqt2oJK7eiwubi6YXXt8RHR1BnzBs` |
| JST token (testnet) | `JST` | `TJqk3ChKSjmpoNm3gaqSEatNsueD37NGDK` |
| WJST (voting wrapper, testnet) | `WJST` | `TCxA1eNhsAV3gvUwLjLtREW9f775V4h1h7` |
| StakedTRX proxy (testnet) | `sTRX` | `TZ8du1HkatTWDbS6FLZei4dQfjfpSm9mxp` |

The Nile testnet currently exposes a subset of the mainnet jToken markets plus four QA-only markets (`jUSD1test`, `jETHQA`, `jBUSDqa1`, `jBUSDqa2`). For the complete Nile jToken list with delegator and underlying addresses, see [`contracts.json` → `networks.nile`](contracts.json) or the [MCP server `chains.ts`](https://github.com/justlend/mcp-server-justlend/blob/main/src/core/chains.ts).

### Configuring clients for Nile

```bash
# JustLend Skills / MCP server
export NETWORK=nile
```

```javascript
// TronWeb
const tronWeb = new TronWeb({
  fullHost: 'https://nile.trongrid.io',
  // ...
});
```

Tronscan testnet explorer: <https://nile.tronscan.org>.
