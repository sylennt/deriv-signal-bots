# api.py

from deriv_api import DerivAPI
from config import APP_ID, API_TOKEN

api = DerivAPI(app_id=APP_ID)


async def connect():
    await api.authorize(API_TOKEN)


async def get_candles(symbol: str, timeframe: int, count: int = 100):
    response = await api.ticks_history({
        "ticks_history": symbol,
        "adjust_start_time": 1,
        "count": count,
        "end": "latest",
        "style": "candles",
        "granularity": timeframe
    })

    return response["candles"]

