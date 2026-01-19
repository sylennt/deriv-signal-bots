from api import get_candles
from structure import support_resistance, liquidity_sweep


def analyze(symbol, balance=100, risk_percent=1):
    candles_4h = get_candles(symbol, 14400)
    candles_1h = get_candles(symbol, 3600)
    candles_15m = get_candles(symbol, 900)

    if not candles_4h or not candles_1h or not candles_15m:
        return None

    support, resistance = support_resistance(candles_1h)
    sweep = liquidity_sweep(candles_15m)

    if sweep is None:
        return None

    entry = float(candles_15m[-1]["close"])

    if sweep == "BUY":
        sl = support
        tp = entry + (entry - sl) * 2
    else:
        sl = resistance
        tp = entry - (sl - entry) * 2

    risk_amount = balance * (risk_percent / 100)
    lot_size = round(risk_amount / abs(entry - sl), 2)

    return {
        "symbol": symbol,
        "direction": sweep,
        "entry": round(entry, 2),
        "sl": round(sl, 2),
        "tp": round(tp, 2),
        "lot_size": lot_size
    }
