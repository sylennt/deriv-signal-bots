import pandas as pd
import numpy as np
from api import get_candles


# ==============================
# Helper Functions
# ==============================

def to_df(candles):
    df = pd.DataFrame(candles)
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    return df


def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


def detect_trend(df):
    df["ema50"] = ema(df["close"], 50)
    df["ema200"] = ema(df["close"], 200)

    if df["ema50"].iloc[-1] > df["ema200"].iloc[-1]:
        return "BULLISH"
    elif df["ema50"].iloc[-1] < df["ema200"].iloc[-1]:
        return "BEARISH"
    else:
        return "RANGE"


def break_of_structure(df):
    last_high = df["high"].iloc[-2]
    last_low = df["low"].iloc[-2]
    current_close = df["close"].iloc[-1]

    if current_close > last_high:
        return "BULLISH_BOS"
    elif current_close < last_low:
        return "BEARISH_BOS"
    else:
        return None


def confirmation_candle(df, direction):
    last = df.iloc[-1]

    if direction == "BUY":
        return last["close"] > last["open"]
    elif direction == "SELL":
        return last["close"] < last["open"]

    return False


# ==============================
# Main Strategy Function
# ==============================

def analyze(symbol):
    try:
        # Fetch candles
        candles_1h = get_candles(symbol, 3600)
        candles_15m = get_candles(symbol, 900)
        candles_5m = get_candles(symbol, 300)

        if not candles_1h or not candles_15m or not candles_5m:
            print(f"No candle data for {symbol}")
            return None

        df_1h = to_df(candles_1h)
        df_15m = to_df(candles_15m)
        df_5m = to_df(candles_5m)

        # 1H Trend Bias
        trend = detect_trend(df_1h)

        # 15M Break of Structure
        bos = break_of_structure(df_15m)

        # Determine trade direction
        signal = None

        if trend == "BULLISH" and bos == "BULLISH_BOS":
            signal = "BUY"

        elif trend == "BEARISH" and bos == "BEARISH_BOS":
            signal = "SELL"

        if signal is None:
            print(f"No setup for {symbol}")
            return None

        # 5M Confirmation
        if not confirmation_candle(df_5m, signal):
            print(f"No 5M confirmation for {symbol}")
            return None

        # Entry and Risk Management
        entry = df_5m["close"].iloc[-1]

        if signal == "BUY":
            stop_loss = df_5m["low"].iloc[-2]
            take_profit = entry + (entry - stop_loss) * 2  # 1:2 RR
        else:
            stop_loss = df_5m["high"].iloc[-2]
            take_profit = entry - (stop_loss - entry) * 2  # 1:2 RR

        return {
            "symbol": symbol,
            "signal": signal,
            "entry": round(entry, 2),
            "stop_loss": round(stop_loss, 2),
            "take_profit": round(take_profit, 2),
            "reason": "1H EMA trend + 15M BOS + 5M confirmation"
        }

    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return None
