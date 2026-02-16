import os
import requests

def send_telegram_alert(trade):

    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")

    if not bot_token or not chat_id:
        print("Missing BOT_TOKEN or CHAT_ID")
        return

    symbol = trade.get("symbol", "UNKNOWN")

    message = (
        f"📊 Pair: {symbol}\n"
        f"Signal: {trade['signal']}\n"
        f"Entry: {trade['entry']}\n"
        f"Stop Loss: {trade['stop_loss']}\n"
        f"Take Profit: {trade['take_profit']}\n"
        f"Reason: {trade['reason']}"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    response = requests.post(url, data={
        "chat_id": chat_id,
        "text": message
    })

    print("Status:", response.status_code)
    print("Response:", response.text)
