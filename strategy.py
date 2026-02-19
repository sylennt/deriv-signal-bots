import pandas as pd
from api import get_candles
from utils import to_df

RR_RATIO = 2.5   # Between 1:2 and 1:3


def add_ema(df, period=50):
    df["ema"] = df["close"].ewm(span=period, adjust=False).mean()
    return df


def detect_trend(df):
    """
    1H trend bias using EMA + structure.
    """
    df = add_ema(df)

    last_close = df["close"].iloc[-1]
    ema = df["ema"].iloc[-1]

    if last_close > ema:
        return "BUY"
    elif last_close < ema:
        return "SELL"

    return None


def pullback_confirmation(df, direction):
    """
    15M pullback into EMA zone.
    """
    df = add_ema(df)

    last_close = df["close"].iloc[-1]
    ema = df["ema"].iloc[-1]

    # Allow small tolerance to increase frequency
    tolerance = ema * 0.002

    if direction == "BUY":
        if last_close <= ema + tolerance:
            return True

    if direction == "SELL":
        if last_close >= ema - tolerance:
            return True

    return False


def break_of_structure(df, direction):
    """
    5M entry trigger using minor structure break.
    """
    if len(df) < 20:
        return False

    recent_high = df["high"].iloc[-6:-1].max()
    recent_low = df["low"].iloc[-6:-1].min()
    last_close = df["close"].iloc[-1]

    if direction == "BUY" and last_close > recent_high:
        return True

    if direction == "SELL" and last_close < recent_low:
        return True

    return False


def calculate_trade(df, direction):
    """
    Calculates entry, SL and TP safely.
    """
    entry = df["close"].iloc[-1]

    if direction == "BUY":
        sl = df["low"].iloc[-5:].min()
        risk = entry - sl
        tp = entry + (risk * RR_RATIO)

        if not (sl < entry < tp):
            return None

    elif direction == "SELL":
        sl = df["high"].iloc[-5:].max()
        risk = sl - entry
        tp = entry - (risk * RR_RATIO)

        if not (tp < entry < sl):
            return None

    else:
        return None

    return {
        "signal": direction,
        "entry": round(entry, 2),
        "stop_loss": round(sl, 2),
        "take_profit": round(tp, 2)
    }


def analyze(symbol):
    """
    Multi-timeframe system:
    1H trend
    15M pullback
    5M break of structure
    """

    try:
        df_1h = to_df(get_candles(symbol, 3600))
        df_15m = to_df(get_candles(symbol, 900))
        df_5m = to_df(get_candles(symbol, 300))
    except Exception as e:
        print(f"Data error for {symbol}: {e}")
        return None

    trend = detect_trend(df_1h)

    if trend is None:
        print(f"No clear trend for {symbol}")
        return None

    if not pullback_confirmation(df_15m, trend):
        print(f"No pullback for {symbol}")
        return None

    if not break_of_structure(df_5m, trend):
        print(f"No entry trigger for {symbol}")
        return None

    trade = calculate_trade(df_5m, trend)

    if trade is None:
        print(f"Invalid SL/TP for {symbol}")
        return None

    trade["symbol"] = symbol
    trade["reason"] = "1H EMA Trend + 15M Pullback + 5M BOS"

    return trade
