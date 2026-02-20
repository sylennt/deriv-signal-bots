# strategy.py

import pandas as pd
import numpy as np
from deriv_api import get_candles


# =========================
# INDICATORS
# =========================

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


def rsi(series, period=14):
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(period).mean()
    avg_loss = pd.Series(loss).rolling(period).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# =========================
# TREND DETECTION (4H)
# =========================

def get_trend(df):
    df["ema50"] = ema(df["close"], 50)
    df["ema200"] = ema(df["close"], 200)

    if df["ema50"].iloc[-1] > df["ema200"].iloc[-1]:
        return "BULLISH"
    elif df["ema50"].iloc[-1] < df["ema200"].iloc[-1]:
        return "BEARISH"
    else:
        return "RANGE"


# =========================
# STRUCTURE CONFIRMATION (1H)
# =========================

def structure_confirm(df, trend):
    recent_high = df["high"].rolling(20).max().iloc[-1]
    recent_low = df["low"].rolling(20).min().iloc[-1]
    current_price = df["close"].iloc[-1]

    if trend == "BULLISH" and current_price > recent_low:
        return True
    if trend == "BEARISH" and current_price < recent_high:
        return True

    return False


# =========================
# ENTRY LOGIC (15M)
# =========================

def entry_signal(df, trend):
    df["rsi"] = rsi(df["close"], 14)
    current_rsi = df["rsi"].iloc[-1]
    current_price = df["close"].iloc[-1]

    if trend == "BULLISH" and current_rsi < 40:
        return "BUY", current_price

    if trend == "BEARISH" and current_rsi > 60:
        return "SELL", current_price

    return None, None


# =========================
# MAIN ANALYZE FUNCTION
# =========================

def analyze(symbol):

    # ---- Fetch Data ----
    df_4h = get_candles(symbol, 14400, 100)
    df_1h = get_candles(symbol, 3600, 150)
    df_15m = get_candles(symbol, 900, 200)

    if df_4h is None or len(df_4h) < 50:
        print(f"Not enough 4H data for {symbol}")
        return None

    if df_1h is None or len(df_1h) < 50:
        print(f"Not enough 1H data for {symbol}")
        return None

    if df_15m is None or len(df_15m) < 50:
        print(f"Not enough 15M data for {symbol}")
        return None

    # ---- Trend ----
    trend = get_trend(df_4h)

    if trend == "RANGE":
        print(f"Ranging market for {symbol}")
        return None

    # ---- Structure ----
    if not structure_confirm(df_1h, trend):
        print(f"Structure mismatch for {symbol}")
        return None

    # ---- Entry ----
    signal, entry_price = entry_signal(df_15m, trend)

    if not signal:
        print(f"No setup for {symbol}")
        return None

    # ---- Stop Loss & Take Profit (1:3 RR) ----
    recent_high = df_15m["high"].rolling(20).max().iloc[-1]
    recent_low = df_15m["low"].rolling(20).min().iloc[-1]

    if signal == "BUY":
        stop_loss = recent_low
        risk = entry_price - stop_loss
        take_profit = entry_price + (risk * 3)

        if stop_loss >= entry_price:
            return None

    else:  # SELL
        stop_loss = recent_high
        risk = stop_loss - entry_price
        take_profit = entry_price - (risk * 3)

        if stop_loss <= entry_price:
            return None

   return {
    "symbol": symbol,
    "signal": signal,
    "entry": round(entry_price, 2),
    "stop_loss": round(stop_loss, 2),
    "take_profit": round(take_profit, 2),
    "trend": trend,
    "rr": "1:3",
    "reason": f"{trend} trend + 15M RSI pullback"
}
