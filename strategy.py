import pandas as pd
from api import get_candles
from utils import to_df


# ==============================
# 4H HIGHER TIMEFRAME BIAS
# ==============================

def higher_timeframe_bias(df):
    ema = df["close"].ewm(span=200).mean()

    if df["close"].iloc[-1] > ema.iloc[-1]:
        return "BUY"
    elif df["close"].iloc[-1] < ema.iloc[-1]:
        return "SELL"

    return "NO_TRADE"


# ==============================
# 1H STRUCTURE CONFIRMATION
# ==============================

def structure_trend(df):
    recent_highs = df["high"].iloc[-5:]
    recent_lows = df["low"].iloc[-5:]

    if recent_highs.is_monotonic_increasing and recent_lows.is_monotonic_increasing:
        return "BUY"

    if recent_highs.is_monotonic_decreasing and recent_lows.is_monotonic_decreasing:
        return "SELL"

    return "NO_TRADE"


# ==============================
# 15M BREAK OF STRUCTURE
# ==============================

def break_of_structure(df, direction):
    recent_high = df["high"].iloc[-10:-1].max()
    recent_low = df["low"].iloc[-10:-1].min()
    current_close = df["close"].iloc[-1]

    if direction == "BUY":
        return current_close > recent_high

    if direction == "SELL":
        return current_close < recent_low

    return False


# ==============================
# 5M CONFIRMATION CANDLE
# ==============================

def confirmation_candle(df, direction):
    candle = df.iloc[-1]

    body = abs(candle["close"] - candle["open"])
    total_range = candle["high"] - candle["low"]

    if total_range == 0:
        return False

    strength = body / total_range

    if direction == "BUY":
        return candle["close"] > candle["open"] and strength > 0.6

    if direction == "SELL":
        return candle["close"] < candle["open"] and strength > 0.6

    return False


# ==============================
# RISK MANAGEMENT (1:2 RR)
# ==============================

def risk_management(entry, sl, balance=10, risk_percent=0.03):
    risk_amount = balance * risk_percent
    risk_per_unit = abs(entry - sl)

    if risk_per_unit == 0:
        return None

    lot_size = risk_amount / risk_per_unit

    # 1:2 Risk Reward
    if entry > sl:
        tp = entry + (2 * risk_per_unit)
    else:
        tp = entry - (2 * risk_per_unit)

    return round(lot_size, 2), round(tp, 2)


# ==============================
# MAIN ANALYZE FUNCTION
# ==============================

def analyze(symbol, balance=10, risk_percent=0.03):
    try:
        # Fetch candles
        df_4h = to_df(get_candles(symbol, 14400))
        df_1h = to_df(get_candles(symbol, 3600))
        df_15m = to_df(get_candles(symbol, 900))
        df_5m = to_df(get_candles(symbol, 300))

        if any(df is None or len(df) < 50 for df in [df_4h, df_1h, df_15m, df_5m]):
            print(f"Not enough data for {symbol}")
            return None

        # 1️⃣ 4H Bias
        bias = higher_timeframe_bias(df_4h)
        if bias == "NO_TRADE":
            print(f"No 4H bias for {symbol}")
            return None

        # 2️⃣ 1H Structure
        structure = structure_trend(df_1h)
        if structure != bias:
            print(f"Structure mismatch for {symbol}")
            return None

        # 3️⃣ 15M BOS
        if not break_of_structure(df_15m, bias):
            print(f"No break of structure for {symbol}")
            return None

        # 4️⃣ 5M Confirmation
        if not confirmation_candle(df_5m, bias):
            print(f"No confirmation candle for {symbol}")
            return None

        # Entry
        entry = df_5m["close"].iloc[-1]

        # Stop loss
        if bias == "BUY":
            sl = df_5m["low"].iloc[-5:].min()
        else:
            sl = df_5m["high"].iloc[-5:].max()

        # Risk Management
        rm = risk_management(entry, sl, balance, risk_percent)
        if rm is None:
            return None

        lot_size, tp = rm

        return {
            "signal": bias,
            "entry": round(entry, 2),
            "stop_loss": round(sl, 2),
            "take_profit": tp,
            "lot_size": lot_size,
            "reason": "4H bias + 1H structure + 15M BOS + 5M confirmation"
        }

    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return None
