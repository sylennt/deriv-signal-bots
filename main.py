from telegram_alert import send_telegram_alert

def run():
    test_trade = {
        "signal": "BUY",
        "entry": 100,
        "stop_loss": 95,
        "take_profit": 110,
        "reason": "Forced test from GitHub"
    }

    send_telegram_alert(test_trade)

if __name__ == "__main__":
    run()
