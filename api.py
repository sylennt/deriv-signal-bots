import websocket
import json

DERIV_WS_URL = "wss://ws.derivws.com/websockets/v3?app_id=1089"


def get_candles(symbol, granularity, count=200):
    ws = websocket.create_connection(DERIV_WS_URL)

    payload = {
        "ticks_history": symbol,
        "adjust_start_time": 1,
        "count": count,
        "end": "latest",
        "granularity": granularity,
        "style": "candles"
    }

    ws.send(json.dumps(payload))
    response = json.loads(ws.recv())
    ws.close()

    if "candles" not in response:
        raise Exception(f"Deriv API error: {response}")

    return response["candles"]
