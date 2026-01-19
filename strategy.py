# strategy.py

import asyncio
from api import get_candles
from config import TIMEFRAME_4H, TIMEFRAME_1H, CANDLE_COUNT


def analyze(symbol: str):
    candles_4h = asyncio.run(
        get_candles(symbol, TIMEFRAME_4H, CANDLE_COUNT)
    )
    candles_1h = asyncio.run(
        get_candles(symbol, TIMEFRAME_1H, CANDLE_COUNT)
    )

    last_4h = candles_4h[-1]
    last_1h = candles_1h[-1]

    # Simple trend logic (placeholder but valid)
    if last_1h["close"] > last_4h["open"]:
        return {
            "signal": "BUY",
            "stop_loss": abs(last_1h["close"] - last_1h["open"])
        }

    if last_1h["close"] < last_4h["open"]:
        return {
            "signal": "SELL",
            "stop_loss": abs(last_1h["open"] - last_1h["close"])
        }

    return {"signal": "NO_TRADE"}

