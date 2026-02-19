import pandas as pd
import numpy as np
from api import get_candles


# ===============================
# Utility
# ===============================

def to_df(candles):
    df = pd.DataFrame(candles)
    df = df.rename(columns={
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close"
    })
    df = df.astype(float)
    return df


# ===============================
# Structure Detection
# ===============================

def detect_trend(df):
    sma_fast = df["Close"].rolling(20).mean()
    sma_slow = df["Close"].rolling(50).mean()

    if sma_fast.iloc[-1] > sma_slow.iloc[-1]:
        return "BULLISH"
    elif sma_fast.iloc[-1] < sma_slow.iloc[-1]:
        return "BEARISH"
    else:
        return "RANGE"


def liquidity_sweep(df):
    recent_high = df["High"].iloc[-10:-1].max()
    recent_low = df["Low"].iloc[-10:-1].min()

    last_high = df["High"].iloc[-1]
    last_low = df["Low"].iloc[-1]
    last_close = df["Close"].iloc[-1]

    # Sweep high and close back inside
    if last_high > recent_high and last_close < recent_high:
        return "SWEEP_HIGH"

    # Sweep low and close back inside
    if last_low < recent_low and last_close > recent_low:
        return "SWEEP_LOW"

    return None


def nearest_structure(df):
    resistance = df["High"].iloc[-20:].max()
    support = df["Low"].iloc[-20:].min()
    return support, resistance


# ===============================
# Risk Management
# ===============================

def calculate_rr(entry, sl, tp):
    risk = abs(entry - sl)
    reward = abs(tp - entry)
    if risk == 0:
        return 0
    return reward / risk


# ===============================
# Main Analysis Function
# ===============================

def analyze(symbol, balance=100, risk_percent=1):

    try:
        # Fetch candles
        df_4h = to_df(get_candles(symbol, 14400))
        df_1h = to_df(get_candles(symbol, 3600))
        df_15m = to_df(get_candles(symbol, 900))
        df_5m = to_df(get_candles(symbol, 300))

    except Exception as e:
        print(f"Data error for {symbol}: {e}")
        return {
            "symbol": symbol,
            "signal": "NO_TRADE"
        }

    trend_4h = detect_trend(df_4h)
    trend_1h = detect_trend(df_1h)

    if trend_4h != trend_1h:
        print(f"Structure mismatch for {symbol}")
        return {
            "symbol": symbol,
            "signal": "NO_TRADE"
        }

    entry_price = df_5m["Close"].iloc[-1]
    sweep = liquidity_sweep(df_15m)
    support, resistance = nearest_structure(df_15m)

    score = 0
    signal = None
    stop_loss = None
    take_profit = None

    # ===============================
    # BUY Setup
    # ===============================
    if trend_4h == "BULLISH" and sweep == "SWEEP_LOW":
        score += 2

        stop_loss = df_5m["Low"].iloc[-5:].min()
        risk = entry_price - stop_loss

        if risk > 0:
            tp2 = entry_price + (risk * 2)
            tp3 = entry_price + (risk * 3)

            # Check if structure allows
            if resistance > tp2:
                take_profit = tp2
                score += 1

            if resistance > tp3:
                take_profit = tp3
                score += 1

            signal = "BUY"

    # ===============================
    # SELL Setup
    # ===============================
    elif trend_4h == "BEARISH" and sweep == "SWEEP_HIGH":
        score += 2

        stop_loss = df_5m["High"].iloc[-5:].max()
        risk = stop_loss - entry_price

        if risk > 0:
            tp2 = entry_price - (risk * 2)
            tp3 = entry_price - (risk * 3)

            if support < tp2:
                take_profit = tp2
                score += 1

            if support < tp3:
                take_profit = tp3
                score += 1

            signal = "SELL"

    # ===============================
    # Final Validation
    # ===============================

    if not signal or score < 3:
        print(f"No setup for {symbol}")
        return {
            "symbol": symbol,
            "signal": "NO_TRADE"
        }

    rr = calculate_rr(entry_price, stop_loss, take_profit)

    if rr < 2:
        print(f"RR too small for {symbol}")
        return {
            "symbol": symbol,
            "signal": "NO_TRADE"
        }

    # Lot sizing
    risk_amount = balance * (risk_percent / 100)
    lot_size = risk_amount / abs(entry_price - stop_loss)

    return {
        "symbol": symbol,
        "signal": signal,
        "entry": round(entry_price, 2),
        "stop_loss": round(stop_loss, 2),
        "take_profit": round(take_profit, 2),
        "rr": round(rr, 2),
        "lot_size": round(lot_size, 2),
        "reason": f"{trend_4h} + Liquidity Sweep + Structure | Score: {score}"
    }
