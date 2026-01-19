from structure import support_resistance, liquidity_sweep

def analyze(candles):
    if not candles or len(candles) < 50:
        return {
            "signal": "NO_TRADE",
            "entry": None,
            "stop_loss": None,
            "take_profit": None,
            "reason": "Not enough data"
        }

    sr = support_resistance(candles)
    liquidity = liquidity_sweep(candles)

    if not sr or not liquidity:
        return {
            "signal": "NO_TRADE",
            "entry": None,
            "stop_loss": None,
            "take_profit": None,
            "reason": "No structure"
        }

    if liquidity["type"] == "BUY":
        return {
            "signal": "BUY",
            "entry": liquidity["price"],
            "stop_loss": sr["support"],
            "take_profit": sr["resistance"],
            "reason": "Liquidity sweep + structure"
        }

    if liquidity["type"] == "SELL":
        return {
            "signal": "SELL",
            "entry": liquidity["price"],
            "stop_loss": sr["resistance"],
            "take_profit": sr["support"],
            "reason": "Liquidity sweep + structure"
        }

    return {
        "signal": "NO_TRADE",
        "entry": None,
        "stop_loss": None,
        "take_profit": None,
        "reason": "Conditions not met"
    }
