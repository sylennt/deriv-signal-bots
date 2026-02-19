import asyncio
import pandas as pd
from api import get_candles
from utils import to_df

RR_RATIO = 2.5        # Between 1:2 and 1:3
SWEEP_TOLERANCE = 0.002   # 0.2% tolerance to increase frequency


def detect_trend(df):
    """
    1H trend detection using swing structure.
    """
    if len(df) < 50:
        return None

    recent = df.tail(30)

    higher_high = recent["high"].iloc[-1] > recent["high"].iloc[-10]
    higher_low = recent["low"].iloc[-1] > recent["low"].iloc[-10]

    lower_high = recent["high"].iloc[-1] < recent["high"].iloc[-10]
    lower_low = recent["low"].iloc[-1] < recent["low"].iloc[-10]

    if higher_high and higher_low:
        return "BUY"

    if lower_high and lower_low:
        return "SELL"

    return None


def liquidity_sweep(df):
    """
    Softer liquidity sweep logic for medium frequency.
    """
    if len(df) < 30:
        return None

    recent_high = df["high"].iloc[-15:-1].max()
    recent_low = df["low"].iloc[-15:-1].min()

    last_candle = df.iloc[-1]

    # BUY sweep (stop hunt below lows)
    if (
        last_candle["low"] <= recent_low * (1 + SWEEP_TOLERANCE)
        and last_candle["close"] > recent_low
    ):
        return "BUY"

    # SELL sweep (stop hunt above highs)
    if (
        last_candle["high"] >= recent_high * (1 - SWEEP_TOLERANCE)
        and last_candle["close"] < recent_high
    ):
        return "SELL"

    return None


def calculate_trade(df, direction):
    """
    Calculates entry, SL and TP with proper alignment.
    """
    entry = df["close"].iloc[-1]

    if direction == "BUY":
        sl = df["low"].iloc[-5:].min()
        risk = entry - sl
        tp = entry + (risk * RR_RATIO)

    elif direction == "SELL":
        sl = df["high"].iloc[-5:].max()
        risk = sl - entry
        tp = entry - (risk * RR_RATIO)

    else:
        return None

    # Safety check to prevent wrong SL/TP direction
    if direction == "BUY" and not (sl < entry < tp):
        return None

    if direction == "SELL" and not (tp < entry < sl):
        return None

    return {
        "signal": direction,
        "entry": round(entry, 2),
        "stop_loss": round(sl, 2),
        "take_profit": round(tp, 2)
    }


def analyze(symbol):
    """
    Multi-timeframe strategy:
    1H trend bias
    15M liquidity sweep zone
    5M entry trigger
    """

    try:
        candles_1h = get_candles(symbol, 3600)
        candles_15m = get_candles(symbol, 900)
        candles_5m = get_candles(symbol, 300)

        df_1h = to_df(candles_1h)
        df_15m = to_df(candles_15m)
        df_5m = to_df(candles_5m)

    except Exception as e:
        print(f"Data error for {symbol}: {e}")
        return None

    trend = detect_trend(df_1h)

    if trend is None:
        print(f"No clear trend for {symbol}")
        return None

    sweep = liquidity_sweep(df_15m)

    if sweep is None:
        print(f"No liquidity sweep for {symbol}")
        return None

    # Trend must match sweep direction
    if trend != sweep:
        print(f"Structure mismatch for {symbol}")
        return None

    trade = calculate_trade(df_5m, trend)

    if trade is None:
        print(f"Invalid SL/TP setup for {symbol}")
        return None

    trade["symbol"] = symbol
    trade["reason"] = "1H Trend + 15M Sweep + 5M Entry"

    return trade

