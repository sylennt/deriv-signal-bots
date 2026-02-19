import pandas as pd
from api import get_candles
from utils import to_df

RR_RATIO = 2.0   # 1:2 risk reward


def add_ema(df, period=50):
    df["ema"] = df["close"].ewm(span=period, adjust=False).mean()
    return df


def detect_trend(df):
    df = add_ema(df)

    if len(df) < 50:
        return None

    last_close = df["close"].iloc[-1]
    ema = df["ema"].iloc[-1]

    if last_close > ema:
        return "BUY"
    elif last_close < ema:
        return "SELL"

    return None


def momentum_confirmation(df, direction):
    """
    15M momentum confirmation using last 3 candles.
    """
    if len(df) < 5:
        return False

    last3 = df["close"].iloc[-3:]
    opens3 = df["open"].iloc[-3:]

    bullish = all(last3 > opens3)
    bearish = all(last3 < opens3)

    if direction == "BUY" and bullish:
        return True

    if direction == "SELL" and bearish:
        return True

    return False


def micro_break(df, direction):
    """
    5M micro structure break
    """
    if len(df) < 10:
        return False

    recent_high = df["high"].iloc[-4:-1].max()
    recent_low = df["low"].iloc[-4:-1].min()
    last_close = df["close"].iloc[-1]

    if direction == "BUY" and last_close > recent_high:
        return True

    if direction == "SELL" and last_close < recent_low:
        return True

    return False


def calculate_trade(df, direction):
    entry = df["close"].iloc[-1]

    if direction == "BUY":
        sl = df["low"].iloc[-4:].min()
        risk = entry - sl

        if risk <= 0:
            return None

        tp = entry + (risk * RR_RATIO)

        if not (sl < entry < tp):
            return None

    elif direction == "SELL":
        sl = df["high"].iloc[-4:].max()
        risk = sl - entry

        if risk <= 0:
            return None

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

    try:
        df_1h = to_df(get_candles(symbol, 3600))
        df_15m = to_df(get_candles(symbol, 900))
        df_5m = to_df(get_candles(symbol, 300))
    except Exception as e:
        print(f"Data error for {symbol}: {e}")
        return None

    trend = detect_trend(df_1h)

    if trend is None:
        print(f"No trend for {symbol}")
        return None

    if not momentum_confirmation(df_15m, trend):
        print(f"No momentum for {symbol}")
        return None

    if not micro_break(df_5m, trend):
        print(f"No entry trigger for {symbol}")
        return None

    trade = calculate_trade(df_5m, trend)

    if trade is None:
        print(f"Invalid SL/TP for {symbol}")
        return None

    trade["symbol"] = symbol
    trade["reason"] = "1H Trend + 15M Momentum + 5M Micro Break"

    return trade
