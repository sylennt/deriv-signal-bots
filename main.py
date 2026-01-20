# main.py

from strategy import analyze
from telegram_alert import send_alert
from formatter import format_signal

SYMBOLS = [
    "R_100",
    "R_75",
    "R_50",
    "BOOM1000",
    "CRASH1000"
]

def run():
    for symbol in SYMBOLS:
        trade = analyze(symbol)

        if trade["signal"] != "NO_TRADE":
            message = format_signal(symbol, trade)
            send_alert(message)
            print(f"Alert sent for {symbol}")
            trade = analyze(candles)
            print("TRADE RESULT:", trade)


if __name__ == "__main__":
    run()
