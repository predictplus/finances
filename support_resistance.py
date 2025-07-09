import pandas_datareader.data as web
import mplfinance as mpf
import datetime
import pandas as pd

def get_period_dates(period_code):
    today = datetime.date.today()
    if period_code == "1w":
        start = today - datetime.timedelta(days=7)
    elif period_code == "1m":
        start = today - datetime.timedelta(days=30)
    elif period_code == "3m":
        start = today - datetime.timedelta(days=90)
    elif period_code == "1y":
        start = today - datetime.timedelta(days=365)
    else:
        raise ValueError("Invalid period code")
    return start, today

def resample_df(df, candle_type):
    if candle_type == "1d":
        return df
    freq_map = {
        "1m": "1min",
        "5m": "5min",
        "15m": "15min",
        "30m": "30min",
        "1h": "1H",
        "4h": "4H"
    }
    freq = freq_map.get(candle_type)
    if not freq:
        raise ValueError("Invalid candle type")
    ohlc_dict = {
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }
    df_resampled = df.resample(freq).apply(ohlc_dict).dropna()
    return df_resampled

def plot_candlestick_with_sr(ticker, period_code, candle_type):
    start, end = get_period_dates(period_code)
    df = web.DataReader(ticker, 'stooq', start, end)
    if df.empty:
        print("No data")
        return
    df = df.sort_index()
    if candle_type != "1d":
        df = df.copy()
        df.index = pd.to_datetime(df.index)
        df = resample_df(df, candle_type)
        if df.empty:
            print("No data after resampling")
            return
    min_price = df['Low'].min()
    max_price = df['High'].max()
    apds = [
        mpf.make_addplot([min_price]*len(df), type='line', color='g', width=1, panel=0),
        mpf.make_addplot([max_price]*len(df), type='line', color='r', width=1, panel=0)
    ]
    mpf.plot(
        df,
        type='candle',
        style='charles',
        addplot=apds,
        title=f"{ticker.upper()} - {period_code} Candlestick ({candle_type}) Chart with Support/Resistance",
        ylabel="Price",
        volume=True,
        figratio=(14,7),
        tight_layout=True
    )

if __name__ == "__main__":
    ticker = input("Enter share ticker (e.g., AAPL): ").strip().upper()
    period_code = input("Enter period (1w, 1m, 3m, 1y): ").strip()
    candle_type = input("Enter candlestick type (1m, 5m, 15m, 30m, 1h, 4h, 1d): ").strip()
    plot_candlestick_with_sr(ticker, period_code, candle_type)
