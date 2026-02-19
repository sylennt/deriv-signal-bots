import pandas as pd
import numpy as np
from deriv_api import get_candles


# =========================
# Indicator Functions
# =========================

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


def rsi(series, period=14):
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    gain_avg = pd.Series(gain).rolling(period).mean()
    loss_avg = pd.Series(loss).rolling(period).mean()

    rs = gain_avg / loss_avg
    return 100 - (100 / (1 + rs))


def atr(df, period=14):
    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift())
    low_close = np.abs(df["low"] - df["close"].shift())

    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)

    return true_range.rolling(period).mean()


# =========================
# Main Analysis Function
# =========================

def analyze(symbol):

    try:
        # Get 4H candles (trend)
        df_4h = get_candles(symbol, granularity=14400)
        if df_4h is None or len(df_4h) < 210:
            print(f"Not enough 4H data for {symbol}")
            return None

        # Get 5M candles (entry)
        df_5m = get_candles(symbol, granularity=300)
        if df_5m is None or len(df_5m) < 210:
            print(f"Not enough 5M data for {symbol}")
            return None

    except Exception as e:
        print(f"Data error for {symbol}: {e}")
        return None

    # =========================
    # 4H TREND
    # =========================

    df_4h["ema50"] = ema(df_4h["close"], 50)
    df_4h["ema200"] = ema(df_4h["close"], 200)

    trend = None

    if df_4h["ema50"].iloc[-1] > df_4h["ema200"].iloc[-1]:
        trend = "BUY"
    elif df_4h["ema50"].iloc[-1] < df_4h["ema200"].iloc[-1]:
        trend = "SELL"
    else:
        print(f"No clear 4H trend for {symbol}")
        return None

    # =========================
    # 5M ENTRY LOGIC
    # =========================

    df_5m["ema20"] = ema(df_5m["close"], 20)
    df_5m["rsi"] = rsi(df_5m["close"])
    df_5m["atr"] = atr(df_5m)

    last = df_5m.iloc[-1]
    prev = df_5m.iloc[-2]

    entry_price = last["close"]
    atr_value = last["atr"]

    if np.isnan(atr_value):
        return None

    # =========================
    # BUY SETUP
    # =========================

    if trend == "BUY":

        pullback = last["close"] > last["ema20"] and prev["close"] <= prev["ema20"]
        rsi_ok = 45 <= last["rsi"] <= 65

        if pullback and rsi_ok:

            stop_loss = entry_price - (atr_value * 1.2)
            take_profit = entry_price + ((entry_price - stop_loss) * 3)

            return {
                "symbol": symbol,
                "signal": "BUY",
                "entry": round(entry_price, 2),
                "stop_loss": round(stop_loss, 2),
                "take_profit": round(take_profit, 2),
                "reason": "4H Uptrend + 5M EMA Pullback + RSI Confirmation"
            }

    # =========================
    # SELL SETUP
    # =========================

    if trend == "SELL":

        pullback = last["close"] < last["ema20"] and prev["close"] >= prev["ema20"]
        rsi_ok = 35 <= last["rsi"] <= 55

        if pullback and rsi_ok:

            stop_loss = entry_price + (atr_value * 1.2)
            take_profit = entry_price - ((stop_loss - entry_price) * 3)

            return {
                "symbol": symbol,
                "signal": "SELL",
                "entry": round(entry_price, 2),
                "stop_loss": round(stop_loss, 2),
                "take_profit": round(take_profit, 2),
                "reason": "4H Downtrend + 5M EMA Pullback + RSI Confirmation"
            }

    print(f"No setup for {symbol}")
    return None
