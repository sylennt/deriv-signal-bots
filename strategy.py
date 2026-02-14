from api import get_candles
from structure import support_resistance, liquidity_sweep


def analyze(symbol):
    candles = get_candles(symbol)

    if not candles or len(candles) < 50:
        return {
            "signal": "NO_TRADE",
            "reason": "Not enough data"
        }

    sr = support_resistance(candles)
    liquidity = liquidity_sweep(candles)

    if not sr or not liquidity:
        return {
            "signal": "NO_TRADE",
            "reason": "No structure or no liquidity sweep"
        }

    entry = liquidity["price"]

    # BUY setup
    if liquidity["type"] == "BUY":
        stop_loss = sr["support"]
        take_profit = sr["resistance"]

    # SELL setup
    elif liquidity["type"] == "SELL":
        stop_loss = sr["resistance"]
        take_profit = sr["support"]

    else:
        return {
            "signal": "NO_TRADE",
            "reason": "Invalid liquidity type"
        }

    # Risk Reward Protection
    risk = abs(entry - stop_loss)
    reward = abs(take_profit - entry)

    if risk == 0 or reward / risk < 1.5:
        return {
            "signal": "NO_TRADE",
            "reason": "Bad risk reward"
        }

    return {
        "symbol": symbol,
        "signal": liquidity["type"],
        "entry": round(entry, 2),
        "stop_loss": round(stop_loss, 2),
        "take_profit": round(take_profit, 2),
        "reason": "Liquidity sweep + Support/Resistance confirmation"
    }
