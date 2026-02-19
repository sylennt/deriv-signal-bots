import pandas as pd
import numpy as np
from api import get_candles


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
    rsi = 100 - (100 / (1 + rs))

    return rsi


def to_df(candles):
    df = pd.DataFrame(candles)
    df = df.astype(float)
    return df


# =========================
# MAIN STRATEGY
# =========================

def analyze(symbol):

    try:
        candles_1h = to_df(get_candles(symbol, 3600))
        candles_15m = to_df(get_candles(symbol, 900))
        candles_5m = to_df(get_candles(symbol, 300))
    except Exception as e:
        print(f"Data error for {symbol}: {e}")
        return None

    if len(candles_1h) < 60 or len(candles_15m) < 60 or len(candles_5m) < 20:
        print(f"Not enough data for {symbol}")
        return None

    # =========================
    # 1H TREND
    # =========================

    candles_1h["ema50"] = ema(candles_1h["close"], 50)

    last_1h = candles_1h.iloc[-1]

    if last_1h["close"] > last_1h["ema50"]:
        trend = "BUY"
    elif last_1h["close"] < last_1h["ema50"]:
        trend = "SELL"
    else:
        print(f"No clear trend for {symbol}")
        return None

    # =========================
    # 15M RSI PULLBACK
    # =========================

    candles_15m["rsi"] = rsi(candles_15m["close"], 14)

    rsi_now = candles_15m["rsi"].iloc[-1]
    rsi_prev = candles_15m["rsi"].iloc[-2]

    if trend == "BUY":
        if not (rsi_now < 45 and rsi_now > rsi_prev):
            print(f"No RSI pullback for {symbol}")
            return None

    if trend == "SELL":
        if not (rsi_now > 55 and rsi_now < rsi_prev):
            print(f"No RSI pullback for {symbol}")
            return None

    # =========================
    # 5M ENTRY CONFIRMATION
    # =========================

    last = candles_5m.iloc[-1]
    prev = candles_5m.iloc[-2]

    if trend == "BUY":
        if last["high"] <= prev["high"]:
            print(f"No break confirmation for {symbol}")
            return None

        entry = last["close"]
        stop_loss = candles_5m["low"].iloc[-5:].min()

        if stop_loss >= entry:
            return None

        risk = entry - stop_loss
        take_profit = entry + (risk * 2)

    else:  # SELL
        if last["low"] >= prev["low"]:
            print(f"No break confirmation for {symbol}")
            return None

        entry = last["close"]
        stop_loss = candles_5m["high"].iloc[-5:].max()

        if stop_loss <= entry:
            return None

        risk = stop_loss - entry
        take_profit = entry - (risk * 2)

    # =========================
    # RETURN SIGNAL
    # =========================

    return {
        "symbol": symbol,
        "signal": trend,
        "entry": round(entry, 2),
        "stop_loss": round(stop_loss, 2),
        "take_profit": round(take_profit, 2),
        "reason": "1H Trend + 15M RSI Pullback + 5M Break"
    }
