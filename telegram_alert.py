import requests

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_telegram_alert(trade):
    message = f"""
📊 *DERIV SIGNAL*

Signal: {trade['signal']}
Entry: {trade['entry']}
Stop Loss: {trade['stop_loss']}
Take Profit: {trade['take_profit']}

Reason: {trade['reason']}
"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    requests.post(url, data=payload)
