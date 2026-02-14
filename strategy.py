from api import get_candles
from structure import support_resistance, liquidity_sweep


def analyze(symbol):

    candles = get_candles(symbol, 900)

    if not candles or len(candles) < 50:
        print(f"No setup for {symbol}")
        return None

    sr = support_resistance(candles)
    liquidity = liquidity_sweep(candles)

    # Ensure liquidity is valid dictionary
    if not isinstance(liquidity, dict):
        print(f"No liquidity sweep for {symbol}")
        return None

    if "type" not in liquidity or "price" not in liquidity:
        print(f"Invalid liquidity format for {symbol}")
        return None

    if not sr or "support" not in sr or "resistance" not in sr:
        print(f"No structure for {symbol}")
        return None

    entry = liquidity["price"]

    if liquidity["type"] == "BUY":
        stop_loss = sr["support"]
        take_profit = sr["resistance"]

    elif liquidity["type"] == "SELL":
        stop_loss = sr["resistance"]
        take_profit = sr["support"]

    else:
        print(f"No valid signal for {symbol}")
        return None

    risk = abs(entry - stop_loss)
    reward = abs(take_profit - entry)

    if risk == 0:
        return None

    rr = reward / risk

    if rr < 1.5:
        print(f"Bad RR for {symbol}")
        return None

    return {
        "symbol": symbol,
        "signal": liquidity["type"],
        "entry": round(entry, 2),
        "stop_loss": round(stop_loss, 2),
        "take_profit": round(take_profit, 2),
        "reason": "Liquidity sweep + SR"
    }
