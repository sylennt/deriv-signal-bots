import os
import requests

def send_telegram_alert(trade):

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")

    print("BOT_TOKEN inside function:", BOT_TOKEN)
    print("CHAT_ID inside function:", CHAT_ID)

    if not BOT_TOKEN or not CHAT_ID:
        print("Missing BOT_TOKEN or CHAT_ID")
        return

    message = f"""
Signal: {trade['signal']}
Entry: {trade['entry']}
Stop Loss: {trade['stop_loss']}
Take Profit: {trade['take_profit']}
Reason: {trade['reason']}
"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        }
    )

    print("Telegram response status:", response.status_code)
    print("Telegram response text:", response.text)

