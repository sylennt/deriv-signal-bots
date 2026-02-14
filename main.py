from strategy import analyze
from telegram_alert import send_telegram_alert

SYMBOLS = [
    "R_100",
    "R_75",
    "R_50",
    "BOOM1000",
    "BOOM500",
    "CRASH1000",
    "CRASH500"
]

def run():
    for symbol in SYMBOLS:
        trade = analyze(symbol)

        if trade and trade["signal"] != "NO_TRADE":
            print(f"Signal found for {symbol}")
            send_telegram_alert(trade)
        else:
            print(f"No setup for {symbol}")

if __name__ == "__main__":
    run()
