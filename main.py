from strategy import analyze
from telegram_alert import send_telegram_alert

SYMBOLS = ["R_100", "R_75", "R_50"]

def run():
    for symbol in SYMBOLS:
        trade = analyze(symbol)

        if trade and trade["signal"] != "NO_TRADE":
            send_telegram_alert(trade)

if __name__ == "__main__":
    run()
