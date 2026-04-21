import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def run_trading_bot():
    print(f"--- Running Bitcoin Trading Bot at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")

    # Fetch 60 days of historical Bitcoin data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)

    try:
        btc = yf.download("BTC-USD", start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), progress=False)

        if btc.empty:
            print("Error: Could not fetch data from yfinance.")
            return

        # Calculate Moving Averages on Close prices
        df = btc[['Close']].copy()

        # yf.download can return a MultiIndex if multiple tickers are given, or a regular index for one.
        # Since pandas 2.2+ multi-indexes for single tickers might occur depending on yfinance version,
        # let's try to flatten it safely if needed.
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df['7_day_MA'] = df['Close'].rolling(window=7).mean()
        df['30_day_MA'] = df['Close'].rolling(window=30).mean()

        # Get latest data
        current_price = df['Close'].iloc[-1].item() if hasattr(df['Close'].iloc[-1], 'item') else df['Close'].iloc[-1]
        current_ma7 = df['7_day_MA'].iloc[-1].item() if hasattr(df['7_day_MA'].iloc[-1], 'item') else df['7_day_MA'].iloc[-1]
        current_ma30 = df['30_day_MA'].iloc[-1].item() if hasattr(df['30_day_MA'].iloc[-1], 'item') else df['30_day_MA'].iloc[-1]

        prev_ma7 = df['7_day_MA'].iloc[-2].item() if hasattr(df['7_day_MA'].iloc[-2], 'item') else df['7_day_MA'].iloc[-2]
        prev_ma30 = df['30_day_MA'].iloc[-2].item() if hasattr(df['30_day_MA'].iloc[-2], 'item') else df['30_day_MA'].iloc[-2]

        print(f"Current BTC Price: ${current_price:.2f}")
        print(f"7-Day MA:          ${current_ma7:.2f}")
        print(f"30-Day MA:         ${current_ma30:.2f}")
        print("-" * 40)

        # Determine Signal
        signal = "HOLD"
        reason = "No crossover detected."

        if pd.isna(current_ma30) or pd.isna(prev_ma30):
            signal = "HOLD"
            reason = "Not enough data for 30-day MA."
        elif prev_ma7 <= prev_ma30 and current_ma7 > current_ma30:
            signal = "BUY"
            reason = "Golden Cross! 7-day MA crossed ABOVE 30-day MA."
        elif prev_ma7 >= prev_ma30 and current_ma7 < current_ma30:
            signal = "SELL"
            reason = "Death Cross! 7-day MA crossed BELOW 30-day MA."

        print(f"ACTION SIGNAL: {signal}")
        print(f"REASON: {reason}")
        print("-" * 40)

    except Exception as e:
        print(f"An error occurred during execution: {e}")

if __name__ == "__main__":
    run_trading_bot()