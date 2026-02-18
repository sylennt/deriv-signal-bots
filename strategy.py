import pandas as pd
import numpy as np
from api import get_candles


# ===============================
# Helper Functions
# ===============================

def to_df(candles):
    df = pd.DataFrame(candles)
    df = df.rename(columns={
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close"
    })
    return df


def trend_direction(df):
    ema_20 = df["Close"].ewm(span=20).mean()
    ema_50 = df["Close"].ewm(span=50).mean()

    if ema_20.iloc[-1] > ema_50.iloc[-1]:
        return "UP"
    elif ema_20.iloc[-1] < ema_50.iloc[-1]:
        return "DOWN"
    else:
        return "RANGE"


def liquidity_sweep(df):
    recent_high = df["High"].iloc[-6:-1].max()
    recent_low = df["Low"].iloc[-6:-1].min()

    last_candle = df.iloc[-1]

    if last_candle["Low"] < recent_low:
        return "BUY"
    elif last_candle["High"] > recent_high:
        return "SELL"
    else:
        return None


def momentum_confirmation(df, direction):
    last_close = df["Close"].iloc[-1]
    prev_close = df["Close"].iloc[-2]

    if direction == "BUY" and last_close > prev_close:
        return True
    if direction == "SELL" and last_close < prev_close:
        return True

    return False


def calculate_rr(entry, sl, tp):
    risk = abs(entry - sl)
    reward = abs(tp - entry)

    if risk == 0:
        return 0

    return reward / risk


# ===============================
# Main Strategy Logic
# ===============================

def analyze(symbol):

    try:
        candles_4h = get_candles(symbol, 14400)
        candles_1h = get_candles(symbol, 3600)
        candles_15m = get_candles(symbol, 900)
        candles_5m = get_candles(symbol, 300)

    except Exception as e:
        print(f"Data error for {symbol}: {e}")
        return {"symbol": symbol, "signal": "NO_TRADE"}

    df_4h = to_df(candles_4h)
    df_1h = to_df(candles_1h)
    df_15m = to_df(candles_15m)
    df_5m = to_df(candles_5m)

    trend_4h = trend_direction(df_4h)
    trend_1h = trend_direction(df_1h)

    if trend_4h == "RANGE":
        print(f"No clear HTF trend for {symbol}")
        return {"symbol": symbol, "signal": "NO_TRADE"}

    sweep = liquidity_sweep(df_15m)

    if not sweep:
        print(f"No liquidity sweep for {symbol}")
        return {"symbol": symbol, "signal": "NO_TRADE"}

    score = 0

    # 4H Bias alignment
    if sweep == "BUY" and trend_4h == "UP":
        score += 1
    if sweep == "SELL" and trend_4h == "DOWN":
        score += 1

    # 1H confirmation (soft filter)
    if sweep == "BUY" and trend_1h == "UP":
        score += 1
    if sweep == "SELL" and trend_1h == "DOWN":
        score += 1

    # 5M momentum confirmation
    if momentum_confirmation(df_5m, sweep):
        score += 1

    if score < 2:
        print(f"Setup too weak for {symbol}")
        return {"symbol": symbol, "signal": "NO_TRADE"}

    entry = df_5m["Close"].iloc[-1]

    if sweep == "BUY":
        sl = df_15m["Low"].iloc[-6:-1].min()
        tp = entry + (entry - sl) * 2   # 1:2 RR
    else:
        sl = df_15m["High"].iloc[-6:-1].max()
        tp = entry - (sl - entry) * 2   # 1:2 RR

    rr = calculate_rr(entry, sl, tp)

    if rr < 2:
        print(f"RR too small for {symbol}")
        return {"symbol": symbol, "signal": "NO_TRADE"}

    print(f"Valid setup for {symbol}")

    return {
        "symbol": symbol,
        "signal": sweep,
        "entry": round(entry, 2),
        "stop_loss": round(sl, 2),
        "take_profit": round(tp, 2),
        "rr": round(rr, 2),
        "reason": f"{trend_4h} trend + liquidity sweep + momentum confirmation"
    }

