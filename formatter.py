# formatter.py

def format_signal(symbol, trade):
    return f"""
📊 *{symbol} SIGNAL*

🟢 Type: *{trade['signal']}*
🎯 Entry: `{trade['entry']}`
🛑 Stop Loss: `{trade['stop_loss']}`
💰 Take Profit: `{trade['take_profit']}`

⏱ Timeframe:
4H / 1H Bias
15M Entry

⚠️ Risk properly. Not financial advice.
"""
