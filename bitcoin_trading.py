import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(20)

# Parameters for Geometric Brownian Motion
days = 60
dt = 1 # 1 day
mu = 0.0005 # Expected daily return (slight upward drift)
sigma = 0.03 # Daily volatility (approx 3% daily for Bitcoin)
initial_price = 50000

# Simulate prices
prices = [initial_price]
for _ in range(1, days):
    # GBM formula
    shock = np.random.normal(0, 1)
    drift = (mu - 0.5 * sigma**2) * dt
    diffusion = sigma * np.sqrt(dt) * shock
    price = prices[-1] * np.exp(drift + diffusion)
    prices.append(price)

# Create DataFrame
dates = pd.date_range(start="2023-01-01", periods=days)
df = pd.DataFrame({'Date': dates, 'Price': prices})

# Calculate Moving Averages
df['7_day_MA'] = df['Price'].rolling(window=7).mean()
df['30_day_MA'] = df['Price'].rolling(window=30).mean()

# Trading Algorithm
initial_portfolio_value = 100000.0
cash = initial_portfolio_value
btc_holdings = 0.0

print("Daily Ledger of Trades:")
print("-" * 60)

for i in range(len(df)):
    date = df.loc[i, 'Date'].strftime('%Y-%m-%d')
    price = df.loc[i, 'Price']
    ma7 = df.loc[i, '7_day_MA']
    ma30 = df.loc[i, '30_day_MA']

    # Check if we have MA data (skip initial days where MA30 is not available)
    if pd.isna(ma7) or pd.isna(ma30):
        continue

    # Previous day's MAs to detect crosses
    prev_ma7 = df.loc[i-1, '7_day_MA']
    prev_ma30 = df.loc[i-1, '30_day_MA']

    if pd.isna(prev_ma7) or pd.isna(prev_ma30):
        continue

    # Golden Cross: 7-day MA crosses above 30-day MA
    if prev_ma7 <= prev_ma30 and ma7 > ma30:
        if cash > 0:
            btc_bought = cash / price
            btc_holdings += btc_bought
            print(f"{date}: BUY  {btc_bought:.4f} BTC @ ${price:.2f} | Total Value: ${btc_holdings*price:.2f}")
            cash = 0.0

    # Death Cross: 7-day MA crosses below 30-day MA
    elif prev_ma7 >= prev_ma30 and ma7 < ma30:
        if btc_holdings > 0:
            cash_from_sale = btc_holdings * price
            print(f"{date}: SELL {btc_holdings:.4f} BTC @ ${price:.2f} | Total Value: ${cash_from_sale:.2f}")
            cash = cash_from_sale
            btc_holdings = 0.0

print("-" * 60)

# Final portfolio performance
final_price = df.iloc[-1]['Price']
final_portfolio_value = cash + btc_holdings * final_price
roi = ((final_portfolio_value - initial_portfolio_value) / initial_portfolio_value) * 100

print(f"Initial Portfolio Value: ${initial_portfolio_value:.2f}")
print(f"Final Portfolio Value:   ${final_portfolio_value:.2f}")
print(f"Return on Investment:    {roi:.2f}%")
