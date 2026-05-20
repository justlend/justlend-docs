# Deployed Contracts

!!! info "Network: TRON Mainnet"
    Every address on this page is deployed on **TRON Mainnet** (Chain ID `0x2b6653dc`). For **Nile testnet**, see the [`src/core/chains.ts`](https://github.com/justlend/mcp-server-justlend/blob/main/src/core/chains.ts) configuration in the JustLend MCP server repository.

!!! tip "Machine-readable ABIs"
    Tronscan provides verified-contract ABIs on the **Contract** tab of each link below — click the "ABI" sub-tab to copy or download. Programmatic consumers can also use the bundled ABIs in [`src/core/abis.ts`](https://github.com/justlend/mcp-server-justlend/blob/main/src/core/abis.ts) of the MCP server (TypeScript), which covers jToken, Comptroller, PriceOracle, and TRC20.

!!! warning "Decimals / precision"
    The Compound V2 architecture treats every token amount in **its underlying's smallest unit**. Always read `decimals()` on the underlying TRC20 before constructing `mint`, `borrow`, `repayBorrow`, or `redeemUnderlying` amounts. Common cases: TRX/USDT/USDC = 6, USDD/ETH = 18, BTC/WBTC = 8. jToken amounts (`redeem`, `transfer`) use **8 decimals** regardless of the underlying.

---

## Supply and Borrow Market — Core

| Component | Contract | Address | Tronscan |
|-----------|----------|---------|----------|
| Comptroller (proxy) | `Unitroller` | `TGjYzgCyPobsNS9n6WcbdLVR9dH7mWqFx7` | [Contract](https://tronscan.org/#/contract/TGjYzgCyPobsNS9n6WcbdLVR9dH7mWqFx7) |
| Comptroller (impl) | `Comptroller` | `TB23wYojvAsSx6gR8ebHiBqwSeABiBMPAr` | [Contract](https://tronscan.org/#/contract/TB23wYojvAsSx6gR8ebHiBqwSeABiBMPAr) |

The entrypoint that users and contracts call is **Unitroller** (the proxy). The implementation address rotates with upgrades.

## Supply and Borrow Market — jToken Markets

The address users interact with for `mint`/`borrow`/`repayBorrow`/`redeem`/`liquidateBorrow` is the **CErc20Delegator** (proxy). The **CErc20Delegate** address is the implementation behind it.

| Market | Underlying TRC20 | CErc20Delegator (entrypoint) | CErc20Delegate (impl) |
|--------|------------------|------------------------------|------------------------|
| jTRX | _native_ | [`TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP`](https://tronscan.org/#/token20/TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP) | NA |
| jUSDT | [`TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t`](https://tronscan.org/#/token20/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t) | [`TXJgMdjVX5dKiQaUi9QobwNxtSQaFqccvd`](https://tronscan.org/#/contract/TXJgMdjVX5dKiQaUi9QobwNxtSQaFqccvd) | [`TLjn59xNM7VEK6VZ3VQ8Y1ipxsdsFka5wZ`](https://tronscan.org/#/contract/TLjn59xNM7VEK6VZ3VQ8Y1ipxsdsFka5wZ) |
| jUSDD | [`TXDk8mbtRbXeYuMNS83CfKPaYYT8XWv9Hz`](https://tronscan.org/#/token20/TXDk8mbtRbXeYuMNS83CfKPaYYT8XWv9Hz) | [`TKFRELGGoRgiayhwJTNNLqCNjFoLBh3Mnf`](https://tronscan.org/#/token20/TKFRELGGoRgiayhwJTNNLqCNjFoLBh3Mnf) | [`TLrEfG4QCbax8MTYgZzmjj4gE8RPVNvUn4`](https://tronscan.org/#/token20/TLrEfG4QCbax8MTYgZzmjj4gE8RPVNvUn4) |
| jUSDC | [`TLZSucJRjnqBKwvQz6n5hd29gbS4P7u7w8`](https://tronscan.org/#/token20/TLZSucJRjnqBKwvQz6n5hd29gbS4P7u7w8) | [`TNSBA6KvSvMoTqQcEgpVK7VhHT3z7wifxy`](https://tronscan.org/#/contract/TNSBA6KvSvMoTqQcEgpVK7VhHT3z7wifxy) | [`THQY8YX19jLFSFg1xhthM5wb7xZvKLCzgq`](https://tronscan.org/#/contract/THQY8YX19jLFSFg1xhthM5wb7xZvKLCzgq) |
| jUSDJ | [`TMwFHYXLJaRUPeW6421aqXL4ZEzPRFGkGT`](https://tronscan.org/#/token20/TMwFHYXLJaRUPeW6421aqXL4ZEzPRFGkGT) | [`TL5x9MtSnDy537FXKx53yAaHRRNdg9TkkA`](https://tronscan.org/#/contract/TL5x9MtSnDy537FXKx53yAaHRRNdg9TkkA) | [`TYSHTEq9NFSgst94saeRvt6rAYgWkqMFbj`](https://tronscan.org/#/contract/TYSHTEq9NFSgst94saeRvt6rAYgWkqMFbj) |
| jTUSD | [`TUpMhErZL2fhh4sVNULAbNKLokS4GjC1F4`](https://tronscan.org/#/token20/TUpMhErZL2fhh4sVNULAbNKLokS4GjC1F4) | [`TSXv71Fy5XdL3Rh2QfBoUu3NAaM4sMif8R`](https://tronscan.org/#/contract/TSXv71Fy5XdL3Rh2QfBoUu3NAaM4sMif8R) | [`THbrSjDsDA2KJRxx8K73tN7vLgaXSUNQFk`](https://tronscan.org/#/contract/THbrSjDsDA2KJRxx8K73tN7vLgaXSUNQFk) |
| jUSD1 | [`TPFqcBAaaUMCSVRCqPaQ9QnzKhmuoLR6Rc`](https://tronscan.org/#/token20/TPFqcBAaaUMCSVRCqPaQ9QnzKhmuoLR6Rc) | [`TBEKggwqFkrc4KckQVR9BLucAmQugafEZf`](https://tronscan.org/#/token20/TBEKggwqFkrc4KckQVR9BLucAmQugafEZf) | [`TRo2exz6ZHn6W3Ey3G93FnzhWvjLPUcR2B`](https://tronscan.org/#/contract/TRo2exz6ZHn6W3Ey3G93FnzhWvjLPUcR2B) |
| jwstUSDT | [`TGkxzkDKyMeq2T7edKnyjZoFypyzjkkssq`](https://tronscan.org/#/token20/TGkxzkDKyMeq2T7edKnyjZoFypyzjkkssq) | [`TD5SdLw5scR6mXgyMK2xKrFJpauDjpKqrW`](https://tronscan.org/#/token20/TD5SdLw5scR6mXgyMK2xKrFJpauDjpKqrW) | [`TUx4cV8FQNR5W4FhtF7mHZwaJMoco2464o`](https://tronscan.org/#/token20/TUx4cV8FQNR5W4FhtF7mHZwaJMoco2464o) |
| jsTRX | [`TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5`](https://tronscan.org/#/token20/TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5) | [`TJQ9rbVe9ei3nNtyGgBL22Fuu2xYjZaLAQ`](https://tronscan.org/#/token20/TJQ9rbVe9ei3nNtyGgBL22Fuu2xYjZaLAQ) | [`TCyNbCipGbAybb8rG4aatEoEnfuYpVYCPP`](https://tronscan.org/#/token20/TCyNbCipGbAybb8rG4aatEoEnfuYpVYCPP) |
| jSUN | [`TSSMHYeV2uE9qYH95DqyoCuNCzEL1NvU3S`](https://tronscan.org/#/token20/TSSMHYeV2uE9qYH95DqyoCuNCzEL1NvU3S) | [`TPXDpkg9e3eZzxqxAUyke9S4z4pGJBJw9e`](https://tronscan.org/#/contract/TPXDpkg9e3eZzxqxAUyke9S4z4pGJBJw9e) | [`TM82erAZJSP7NKc17JdTnzVC8WKJHismWB`](https://tronscan.org/#/contract/TM82erAZJSP7NKc17JdTnzVC8WKJHismWB) |
| jBTT | [`TAFjULxiVgT4qWk6UZwjqwZXTSaGaqnVp4`](https://tronscan.org/#/token20/TAFjULxiVgT4qWk6UZwjqwZXTSaGaqnVp4) | [`TUaUHU9Dy8x5yNi1pKnFYqHWojot61Jfto`](https://tronscan.org/#/token20/TUaUHU9Dy8x5yNi1pKnFYqHWojot61Jfto) | [`TH3x5EqLnPduHNX41MaCCb2UfnfFMLuYwe`](https://tronscan.org/#/token20/TH3x5EqLnPduHNX41MaCCb2UfnfFMLuYwe) |
| jNFT | [`TFczxzPhnThNSqr5by8tvxsdCFRRz6cPNq`](https://tronscan.org/#/token20/TFczxzPhnThNSqr5by8tvxsdCFRRz6cPNq) | [`TFpPyDCKvNFgos3g3WVsAqMrdqhB81JXHE`](https://tronscan.org/#/contract/TFpPyDCKvNFgos3g3WVsAqMrdqhB81JXHE) | [`TLkUdtDBLMfJdXni2iTa4u2DKM53XmDJHi`](https://tronscan.org/#/contract/TLkUdtDBLMfJdXni2iTa4u2DKM53XmDJHi) |
| jJST | [`TCFLL5dx5ZJdKnWuesXxi1VPwjLVmWZZy9`](https://tronscan.org/#/token20/TCFLL5dx5ZJdKnWuesXxi1VPwjLVmWZZy9) | [`TWQhCXaWz4eHK4Kd1ErSDHjMFPoPc9czts`](https://tronscan.org/#/contract/TWQhCXaWz4eHK4Kd1ErSDHjMFPoPc9czts) | [`TQ2sbnmxtR7jrNk4nxz2A8f9sneCqmk6SB`](https://tronscan.org/#/contract/TQ2sbnmxtR7jrNk4nxz2A8f9sneCqmk6SB) |
| jWIN | [`TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7`](https://tronscan.org/#/token20/TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7) | [`TRg6MnpsFXc82ymUPgf5qbj59ibxiEDWvv`](https://tronscan.org/#/contract/TRg6MnpsFXc82ymUPgf5qbj59ibxiEDWvv) | [`TW3GyD3hYkKwzSGytWwWGXpe2a93zCpRzJ`](https://tronscan.org/#/contract/TW3GyD3hYkKwzSGytWwWGXpe2a93zCpRzJ) |
| jBTC | [`TN3W4H6rK2ce4vX9YnFQHwKENnHjoxb3m9`](https://tronscan.org/#/token20/TN3W4H6rK2ce4vX9YnFQHwKENnHjoxb3m9) | [`TLeEu311Cbw63BcmMHDgDLu7fnk9fqGcqT`](https://tronscan.org/#/contract/TLeEu311Cbw63BcmMHDgDLu7fnk9fqGcqT) | [`TVsKSRgRoMcCp798qqRGesXRfzy2MzRjkR`](https://tronscan.org/#/contract/TVsKSRgRoMcCp798qqRGesXRfzy2MzRjkR) |
| jWBTC | [`TYhWwKpw43ENFWBTGpzLHn3882f2au7SMi`](https://tronscan.org/#/token20/TYhWwKpw43ENFWBTGpzLHn3882f2au7SMi) | [`TVyvpmaVmz25z2GaXBDDjzLZi5iR5dBzGd`](https://tronscan.org/#/token20/TVyvpmaVmz25z2GaXBDDjzLZi5iR5dBzGd) | [`TDwUJqxB1962DSfKHWMnEu1sWMGGRvHDB5`](https://tronscan.org/#/contract/TDwUJqxB1962DSfKHWMnEu1sWMGGRvHDB5) |
| jETHB | [`TRFe3hT5oYhjSZ6f3ji5FJ7YCfrkWnHRvh`](https://tronscan.org/#/token20/TRFe3hT5oYhjSZ6f3ji5FJ7YCfrkWnHRvh) | [`TWBxQMb6RD3qmkXUXpNwVCYbL8SHNreru6`](https://tronscan.org/#/token20/TWBxQMb6RD3qmkXUXpNwVCYbL8SHNreru6) | [`TS9fVh58y2RMDnpucGXkbfZhAJxmGafGqe`](https://tronscan.org/#/token20/TS9fVh58y2RMDnpucGXkbfZhAJxmGafGqe) |
| jETH | [`THb4CqiFdwNHsWsQCs4JhzwjMWys4aqCbF`](https://tronscan.org/#/token20/THb4CqiFdwNHsWsQCs4JhzwjMWys4aqCbF) | [`TR7BUFRQeq1w5jAZf1FKx85SHuX6PfMqsV`](https://tronscan.org/#/token20/TR7BUFRQeq1w5jAZf1FKx85SHuX6PfMqsV) | [`TQBvTVisiceDvsQVbLbcYyWQGWP7wtaQnc`](https://tronscan.org/#/contract/TQBvTVisiceDvsQVbLbcYyWQGWP7wtaQnc) |
| jWBTT | [`TKfjV9RNKJJCqPvBtK8L7Knykh7DNWvnYt`](https://tronscan.org/#/token20/TKfjV9RNKJJCqPvBtK8L7Knykh7DNWvnYt) | [`TUY54PVeH6WCcYCd6ZXXoBDsHytN9V5PXt`](https://tronscan.org/#/contract/TUY54PVeH6WCcYCd6ZXXoBDsHytN9V5PXt) | [`TV4WWBqBfn1kd4KmpYeSJpVAfybfrxEN9L`](https://tronscan.org/#/contract/TV4WWBqBfn1kd4KmpYeSJpVAfybfrxEN9L) |
| jBUSDOLD (legacy) | [`TMz2SWatiAtZVVcH2ebpsbVtYwUPT9EdjH`](https://tronscan.org/#/token20/TMz2SWatiAtZVVcH2ebpsbVtYwUPT9EdjH) | [`TLHASseQymmpGQdfAyNjkMXFTJh8nzR2x2`](https://tronscan.org/#/contract/TLHASseQymmpGQdfAyNjkMXFTJh8nzR2x2) | [`TNRUqbYfYv4iizWa1b2kd6ZBaoh5zrg3yk`](https://tronscan.org/#/contract/TNRUqbYfYv4iizWa1b2kd6ZBaoh5zrg3yk) |
| jSUNOLD (legacy) | [`TKkeiboTkxXKJpbmVFbv4a8ov5rAfRDMf9`](https://tronscan.org/#/token20/TKkeiboTkxXKJpbmVFbv4a8ov5rAfRDMf9) | [`TGBr8uh9jBVHJhhkwSJvQN2ZAKzVkxDmno`](https://tronscan.org/#/contract/TGBr8uh9jBVHJhhkwSJvQN2ZAKzVkxDmno) | [`TSCpzKvJfXHj1HW5jKg9dZA8z9aMxxGLd8`](https://tronscan.org/#/contract/TSCpzKvJfXHj1HW5jKg9dZA8z9aMxxGLd8) |

## Interest Rate Models

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

## Price Oracle

| Component | Contract | Address | Tronscan |
|-----------|----------|---------|----------|
| Oracle Proxy | `PriceOracleProxy` | `TCKp2AzuhzV4B4Ahx1ej4mvQgHZ1kH7F7k` | [Contract](https://tronscan.org/#/contract/TCKp2AzuhzV4B4Ahx1ej4mvQgHZ1kH7F7k) |
| Oracle (impl) | `PriceOracle` | `TMiNCmvD3zdsv6mk7niBU6NPBzVNjYMQTV` | [Contract / Code](https://tronscan.org/#/contract/TMiNCmvD3zdsv6mk7niBU6NPBzVNjYMQTV/code) |

Prices are denominated in sun (10⁻⁶ TRX), scaled by `10^(tokenDecimal − 6)`. See [Price Oracle](supply_and_borrow_market/price_oracle.md).

## Governance

| Component | Contract | Address | Tronscan |
|-----------|----------|---------|----------|
| Governor (proxy / entrypoint) | `GovernorBravoDelegator` | `TEqiF5JbhDPD77yjEfnEMncGRZNDt2uogD` | [Contract](https://tronscan.org/#/contract/TEqiF5JbhDPD77yjEfnEMncGRZNDt2uogD) |
| Governor (impl) | `GovernorBravoDelegate` | `TCiQTkxhzwSeXhRsNdHCvrxHRAvpjQn5Dt` | [Contract](https://tronscan.org/#/contract/TCiQTkxhzwSeXhRsNdHCvrxHRAvpjQn5Dt) |
| Time-lock | `Timelock` | `TRWNvb15NmfNKNLhQpxefFz7cNjrYjEw7x` | [Contract](https://tronscan.org/#/contract/TRWNvb15NmfNKNLhQpxefFz7cNjrYjEw7x) |
| JST token | `JST` | `TCFLL5dx5ZJdKnWuesXxi1VPwjLVmWZZy9` | [Token20](https://tronscan.org/#/token20/TCFLL5dx5ZJdKnWuesXxi1VPwjLVmWZZy9) |
| WJST (voting) | `WJST` | `TXk9LnTnLN7oH96H3sKxJayMxLxR9M4ZD6` | [Contract / Code](https://tronscan.org/#/contract/TXk9LnTnLN7oH96H3sKxJayMxLxR9M4ZD6/code) |

See [Governance](supply_and_borrow_market/governance.md) for the proposal lifecycle and voting flow.

## Staked TRX

| Component | Contract | Address | Tronscan |
|-----------|----------|---------|----------|
| StakedTRX | `sTRX` | `TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5` | [Token20](https://tronscan.org/#/token20/TU3kjFuhtEo42tsCBtfYUAZxoqQ4yuSLQ5) |

See [Staked TRX](staked_trx.md) for the contract reference.

## Energy Rental

| Component | Contract | Address | Tronscan |
|-----------|----------|---------|----------|
| EnergyRental | `EnergyRental` | `TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd` | [Contract](https://tronscan.io/#/contract/TU2MJ5Veik1LRAgjeSzEdvmDYx7mefJZvd) |

See [Energy Rental](energy_rental.md) for the contract reference.
