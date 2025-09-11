JustLend DAO integrates the energy rental protocol, which aims to provide users with a more convenient and cheaper way to obtain energy. The energy rental protocol is open to all TRON network users and supports one-to-many renting, enabling users to rent energy not only for themselves but also for others. The user-friendly interface is designed to accommodate users managing multiple orders seamlessly.

When renting energy, you need to specify three key parameters based on your requirements, which are **Rental Amount**, **Rental Duration** and **Receiving Address**.

* **Rental Amount:** the amount of energy you need.
    * The actual energy rented is calculated based on the corresponding proxy TRX amount. Due to market fluctuations, the rented energy amount may experience slight changes during the transaction;
    * **Note:** the energy used will be fully restored after 24 hours and can be used again;
    * If you are not sure about the amount of energy you need, please refer to: One USDT transfer transaction ≈ 120,000 energy. (may fluctuate according to market trading conditions).

* **Rental Duration:** this is the time you need to use the energy.
    * Supports renting by the hour or by the day, with a maximum single rental period of **30** days；
    * Rental duration is calculated at the time of placing the order. Market price fluctuations may result in slight increases or decreases in actual usage time;
    * **Note:** Shorter rental durations are more affected by market price volatility. If the rental duration is less than 3 hours, please be sure to cancel the rent immediately after completing the transaction. This will prevent early liquidation due to price fluctuations and avoid unnecessary losses.

* **Receiving Address:** the address where the rented energy will be allocated.
    * If you rent for yourself, this field is not required. If renting for another address, this field is required.
    * **Note:** Renting for contract addresses is not supported.

### **Placing An Order**
Once the parameters are set, you can place an order to proceed with the transaction. The rental protocol will require a prepayment, which includes **Energy Fee**, **Security Deposit** and **Liquidation Penalty**:

* **Energy Fee:** the energy you use is charged based on the time you use. The longer you use, the more you will be charged.
    * The prepaid amount includes the full Energy Fee for your entire rental period. If you return the energy early, the unused portion of the Energy Fee will be refunded proportionally based on the actual usage time.
      
* **Security Deposit:**  a deposit equivalent to one day’s energy fee will be charged based on the amount of energy you rent.
    * Since it takes 24 hours, or 1 day, for energy to recover after use, the security deposit is charged based on 1 day.
    * when you return to the energy:
        * If the energy has been fully restored, the Security Deposit will be fully refunded;
        * If the energy has been used up, 0.75 days of Security Deposit will be deducted from your account;
        * If part of the energy has been used, your Security Deposit will be deducted proportionally.

* **Liquidation Penalty:** calculated as the amount of TRX delegated * 0.01%, with a minimum deposit of 20 TRX.
    * If the rent order is returned on time, the Liquidation Penalty is fully refunded. If not returned before expiry, the order will be liquidated, and the liquidation penalty will be forfeited to community liquidators as a reward.

**Energy Fee** = Rental Amount * Unit Price * Rental Duration

**Security Deposit** = Rental Amount * Daily Price

**Liquidation Penalty** = Max (Equivalent TRX Delegated * 0.01%, 20 TRX)

After completing the rental transaction, you can manage your orders via the energy rental interface. Options include returning the rent, extending the rent order, viewing the actual energy received, and checking the remaining rental duration.

We recommend users customize their leasing plans based on their specific needs:

* **For single transactions**, we recommend returning the energy immediately after use. This avoids liquidation and helps save on occupation fees.
* **For users with regular daily transactions**, we suggest opting for a long-term hassle-free rental plan by renting energy for 30 days based on daily energy consumption. With the 24-hour full restoration rule, there is no need to rent excessive amounts of energy.

### **Cost Estimation**
To provide a clearer understanding of the costs involved in transferring USDT by renting energy versus directly burning TRX, we present the following cost estimates through two examples:

**Scenario 1: Renting 200k Energy for One Day to Transfer USDT**

After renting 200k energy for one day, the USDT transfer is completed, and the rental is terminated immediately. The costs associated with this scenario are based on the prepayment and potential refund formulas previously outlined.

|                        | Receiver holding USDT | Receiver without USDT | Calculation details                                   | Txn example                                                                                                                                                                                                                                   |
|------------------------|-----------------------|-----------------------|-------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| rent energy cost       | - 65.363749           | - 65.363749           | 65.363749 for rent 200k energy                        | [rentTxn](https://tronscan.org/#/transaction/b8a791fe0ef2025f04a9d47c060b1f731b63b466799b7e6360d1cb070463b962)                                                                                                                                |
| rent energy gas        | - 2.153090            | - 2.153090            | 1.77009 burn for energy; 0.383 burn for bandwidth     | [rentTxn](https://tronscan.org/#/transaction/b8a791fe0ef2025f04a9d47c060b1f731b63b466799b7e6360d1cb070463b962)                                                                                                                                |
| transfer USDT gas      | - 0.345000            | - 0.345000            | 0.345 for USDT bandwidth whatever holding USDT or not | [noUsdtTxn](https://tronscan.org/#/transaction/2b620fd06b3b9128b111fbc1f699de87bf9473b13ef29a6104aa882efd66007c); [holdingUsdtTxn](https://tronscan.org/#/transaction/c0ceca04635d6505554916b6f47c2513c1673364daf283d8e36e17d677ef1173)       |
| return energy gas      | - 0.378000            | - 0.378000            | return txn just burn bandwidth for gas                | [holdingUsdtReturnTxn](https://tronscan.org/#/transaction/d5fe0d5a05cfcc9ceef70d47b85f4acf7109e8e1ff027503fa092cf13124b8d6); [noUsdtTxn](https://tronscan.org/#/transaction/534739159370a9966f5dee98b0045774c9079f8c9c0df583883f7abe5fe0fcf1) |
| refund                 | 60.413664             | 59.262775             | return TRX when end rent                              |                                                                                                                                                                                                                                               |
| total energy rent cost | - 7.826175            | - 8.977064            |                                                       |                                                                                                                                                                                                                                               |
| total cost (in USD)    | - $1.57               | - $1.80               | 0.20USDpreTRX                                         |                                                                                                                                                                                                                                               |

**Scenario 2: Directly Burning TRX to Transfer USDT Without Energy**

In this scenario, TRX is burned directly to facilitate the USDT transfer without renting any energy. The cost incurred here is solely dependent on the amount of TRX burned for the transaction.

|                     | Receiver holding USDT | Receiver without USDT  | Calculation details                                                                              | Txn example                                                                                                                                                                                                                                                                          |
|---------------------|-----------------------|------------------------|--------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| burn TRX cost       | - 27.344700           | - 55.064700            | 130,285 energy for notholding USDT; 64,285 energy for holding USDT; 345 bandwidth cost 0.345 TRX | [transfer to a without USDT address](https://tronscan.org/#/transaction/774e9f5601306ff6ff0b70f76944f37da52528cd7cd64d22b9b0903b447a28e8); [transfer to a holding USDT address](https://tronscan.org/#/transaction/c0ceca04635d6505554916b6f47c2513c1673364daf283d8e36e17d677ef1173) |
| total cost (in USD) | - $5.4689             | - $11.0129             | 0.20USDpreTRX                                                                                    |                                                                                                                                                                                                                                                                                      |


**Comparison Insight**

By comparing these two scenarios, it becomes evident that the cost of using rented energy for transaction cost is significantly lower than the cost of directly burning TRX. Additionally, the presence of USDT in the receiving address affects the computational load of the contract, which in turn impacts the overall transaction cost.

|                  | Receiver holding USDT | Receiver without USDT |
|------------------|-----------------------|-----------------------|
| rent energy cost | $1.57                 | $1.80                 |
| burn TRX cost    | $5.4689               | $ 11.0129             |
| save             | - $3.8989             | - $9.2129             |
