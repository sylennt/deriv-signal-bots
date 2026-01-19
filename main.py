# main.py

import asyncio
from config import SYMBOL, BALANCE, RISK_PERCENT
from api import connect
from strategy import analyze
from risk import calculate_position


def run():
    asyncio.run(connect())

    trade = analyze(SYMBOL)

    if trade["signal"] == "NO_TRADE":
        print("No trade signal.")
        return

    position_size = calculate_position(
        BALANCE,
        RISK_PERCENT,
        trade["stop_loss"]
    )

    print("Signal:", trade["signal"])
    print("Position Size:", position_size)


if __name__ == "__main__":
    run()

