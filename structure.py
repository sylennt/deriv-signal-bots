import pandas as pd


def support_resistance(candles, window=20):
    highs = [float(c["high"]) for c in candles]
    lows = [float(c["low"]) for c in candles]

    resistance = max(highs[-window:])
    support = min(lows[-window:])

    return support, resistance


def liquidity_sweep(candles):
    """
    Simple liquidity sweep logic:
    - Price takes previous high and closes below → sell-side sweep
    - Price takes previous low and closes above → buy-side sweep
    """

    if len(candles) < 3:
        return None

    prev = candles[-2]
    curr = candles[-1]

    prev_high = float(prev["high"])
    prev_low = float(prev["low"])

    curr_high = float(curr["high"])
    curr_low = float(curr["low"])
    curr_close = float(curr["close"])

    # Sell-side liquidity sweep
    if curr_high > prev_high and curr_close < prev_high:
        return "SELL"

    # Buy-side liquidity sweep
    if curr_low < prev_low and curr_close > prev_low:
        return "BUY"

    return None
