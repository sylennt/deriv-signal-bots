import pandas as pd

def to_df(candles):
    if not candles:
        return None

    df = pd.DataFrame(candles)

    # Make sure required columns exist
    required = ["open", "high", "low", "close"]
    for col in required:
        if col not in df.columns:
            return None

    # Convert to float
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)

    return df
