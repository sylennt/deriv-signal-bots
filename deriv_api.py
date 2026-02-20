# deriv_api.py

import asyncio
import json
import websockets
import pandas as pd


DERIV_WS = "wss://ws.derivws.com/websockets/v3?app_id=1089"


async def fetch_candles(symbol, granularity=300, count=200):
    async with websockets.connect(DERIV_WS) as ws:

        request = {
            "ticks_history": symbol,
            "adjust_start_time": 1,
            "count": count,
            "end": "latest",
            "granularity": granularity,
            "style": "candles"
        }

        await ws.send(json.dumps(request))
        response = json.loads(await ws.recv())

        if "error" in response:
            raise Exception(f"Deriv API error: {response}")

        candles = response.get("candles")

        if not candles:
            return None

        df = pd.DataFrame(candles)

        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)

        return df


def get_candles(symbol, granularity=300, count=200):
    try:
        return asyncio.run(fetch_candles(symbol, granularity, count))
    except Exception as e:
        print(f"Data error for {symbol}: {e}")
        return None
