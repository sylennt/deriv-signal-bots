import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_alert(trade):
    if BOT_TOKEN is None or CHAT_ID is None:
        print("Telegram credentials missing")
        return

    message = (
        "DERIV SIGNAL\n\n"
        f"Signal: {trade['signal']}\n"
        f"Entry: {trade['entry']}\n"
        f"Stop Loss: {trade['stop_loss']}\n"
        f"Take Profit: {trade['take_profit']}\n\n"
        f"Reason: {trade['reason']}"
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

    print("Telegram response:", response.text)
