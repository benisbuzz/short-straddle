# Short Straddle Strategy

1. Get hourly values of VIX index for period 10th Nov 2022 to 1st Nov 2024
2. Get hourly values of SPY for period 10th Nov 2022 to 1st Nov 2024
3. Create a function to price a vanilla call/put on SPY given an SPY price, an implied vol, assuming interest rates and dividends are zero
4. Create a function to get the delta of a vanilla call/put on SPY given an SPY price, an implied vol, assuming interest rates and dividends are zero
5. We are going to assume that current VIX gives the 1W implied for SPY
6. Create a short gamma strat where you are short a 1W ATM Straddle on SPY and then you delta hedge the position
7. Keep track of your P&L and all trades over the period
8. You can choose any method you like when deciding when/if to sell options
9. You can implement any delta hedging scheme you want
