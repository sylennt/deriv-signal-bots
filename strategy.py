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

    trend = get_trend(symbol)
    df = get_lower_tf_data(symbol)

    if df is None or len(df) < 50:
        print(f"No setup for {symbol}")
        return None

    rsi = calculate_rsi(df['close'])

    last_close = df['close'].iloc[-1]
    last_rsi = rsi.iloc[-1]

    signal = None

    # BUY condition
    if trend == "BULLISH" and last_rsi < 35:
        signal = "BUY"

    # SELL condition
    elif trend == "BEARISH" and last_rsi > 65:
        signal = "SELL"

    if signal is None:
        print(f"No setup for {symbol}")
        return None

    # Risk management 1:3 RR
    risk = df['close'].rolling(10).std().iloc[-1]

    if signal == "BUY":
        entry_price = last_close
        stop_loss = entry_price - risk
        take_profit = entry_price + (risk * 3)

    else:
        entry_price = last_close
        stop_loss = entry_price + risk
        take_profit = entry_price - (risk * 3)

    print(f"Signal found for {symbol}")

    return {
        "symbol": symbol,
        "signal": signal,
        "entry": round(entry_price, 2),
        "stop_loss": round(stop_loss, 2),
        "take_profit": round(take_profit, 2),
        "trend": trend,
        "rr": "1:3",
        "reason": f"{trend} trend + RSI pullback"
    }
