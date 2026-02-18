import pandas as pd
from api import get_candles


# ==========================================
# Helper Functions
# ==========================================

def to_df(candles):
    df = pd.DataFrame(candles)
    df.rename(columns={
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close"
    }, inplace=True)
    return df


def detect_trend(df):
    """
    Simple structure trend detection using HH/LL logic
    """
    recent_highs = df["High"].iloc[-5:]
    recent_lows = df["Low"].iloc[-5:]

    if recent_highs.is_monotonic_increasing:
        return "UP"

    if recent_lows.is_monotonic_decreasing:
        return "DOWN"

    return "RANGE"


def liquidity_sweep(df):
    """
    Detects stop-hunt above/below recent range
    """
    recent_high = df["High"].iloc[-6:-1].max()
    recent_low = df["Low"].iloc[-6:-1].min()

    last_high = df["High"].iloc[-1]
    last_low = df["Low"].iloc[-1]
    last_close = df["Close"].iloc[-1]

    # Sweep below and close back above = BUY setup
    if last_low < recent_low and last_close > recent_low:
        return "BUY"

    # Sweep above and close back below = SELL setup
    if last_high > recent_high and last_close < recent_high:
        return "SELL"

    return None


# ==========================================
# Main Strategy
# ==========================================

def analyze(symbol):

    try:
        candles_1h = get_candles(symbol, 3600)
        candles_15m = get_candles(symbol, 900)
        candles_5m = get_candles(symbol, 300)

        df_1h = to_df(candles_1h)
        df_15m = to_df(candles_15m)
        df_5m = to_df(candles_5m)

    except Exception as e:
        print(f"Data error for {symbol}: {e}")
        return {"symbol": symbol, "signal": "NO_TRADE"}

    # 1️⃣ Higher timeframe trend
    trend = detect_trend(df_1h)

    # 2️⃣ Liquidity sweep on 15m
    sweep = liquidity_sweep(df_15m)

    if not sweep:
        print(f"No liquidity sweep for {symbol}")
        return {"symbol": symbol, "signal": "NO_TRADE"}

    # 3️⃣ Structure alignment
    if sweep == "BUY" and trend != "UP":
        print(f"Structure mismatch for {symbol}")
        return {"symbol": symbol, "signal": "NO_TRADE"}

    if sweep == "SELL" and trend != "DOWN":
        print(f"Structure mismatch for {symbol}")
        return {"symbol": symbol, "signal": "NO_TRADE"}

    # 4️⃣ Entry from 5m confirmation candle
    entry = df_5m["Close"].iloc[-1]

    # ==========================================
    # SL & TP Calculation (Strict Direction Safe)
    # ==========================================

    if sweep == "BUY":

        sl_candidate = df_15m["Low"].iloc[-6:-1].min()

        # SL must be below entry
        if sl_candidate >= entry:
            print(f"Invalid BUY structure for {symbol}")
            return {"symbol": symbol, "signal": "NO_TRADE"}

        sl = sl_candidate
        risk = entry - sl
        tp = entry + (risk * 2)  # 1:2 RR


    elif sweep == "SELL":

        sl_candidate = df_15m["High"].iloc[-6:-1].max()

        # SL must be above entry
        if sl_candidate <= entry:
            print(f"Invalid SELL structure for {symbol}")
            return {"symbol": symbol, "signal": "NO_TRADE"}

        sl = sl_candidate
        risk = sl - entry
        tp = entry - (risk * 2)  # 1:2 RR


    # ==========================================
    # Final Direction Validation
    # ==========================================

    if sweep == "BUY" and not (sl < entry < tp):
        print(f"Directional mismatch for {symbol}")
        return {"symbol": symbol, "signal": "NO_TRADE"}

    if sweep == "SELL" and not (tp < entry < sl):
        print(f"Directional mismatch for {symbol}")
        return {"symbol": symbol, "signal": "NO_TRADE"}

    # ==========================================
    # Valid Signal
    # ==========================================

    print(f"Valid {sweep} setup for {symbol}")

    return {
        "symbol": symbol,
        "signal": sweep,
        "entry": round(entry, 2),
        "stop_loss": round(sl, 2),
        "take_profit": round(tp, 2),
        "reason": f"{trend} trend + liquidity sweep confirmation"
    }
