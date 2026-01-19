# strategy.py

import asyncio
from api import get_candles
from structure import support_resistance, liquidity_sweep
from config import (
    TIMEFRAME_4H,
    TIMEFRAME_1H,
    CANDLE_COUNT
)


def analyze(symbol: str):
    candles_4h = asyncio.run(
        get_candles(symbol, TIMEFRAME_4H, CANDLE_COUNT)
    )
    candles_1h = asyncio.run(
        get_candles(symbol, TIMEFRAME_1H, CANDLE_COUNT)
    )

    last_4h = candles_4h[-1]
    last_1h = candles_1h[-1]

    # -------- TREND BIAS --------
    if last_1h["close"] > last_4h["open"]:
        bias = "BUY"
    elif last_1h["close"] < last_4h["open"]:
        bias = "SELL"
    else:
        return {"signal": "NO_TRADE"}

    # -------- STRUCTURE --------
    support, resistance = support_resistance(candles_1h)
    liquidity = liquidity_sweep(candles_1h)

    price = last_1h["close"]

    # -------- ENTRY LOGIC --------
    if bias == "BUY" and liquidity == "BUY_LIQUIDITY" and price > support:
        stop_loss = price - support
        take_profit = price + (stop_loss * 2)

        return {
            "signal": "BUY",
            "entry": price,
            "stop_loss": stop_loss,
            "take_profit": take_profit
        }

    if bias == "SELL" and liquidity == "SELL_LIQUIDITY" and price < resistance:
        stop_loss = resistance - price
        take_profit = price - (stop_loss * 2)

        return {
            "signal": "SELL",
            "entry": price,
            "stop_loss": stop_loss,
            "take_profit": take_profit
        }

    return {"signal": "NO_TRADE"}
