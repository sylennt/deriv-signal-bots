# risk.py

def calculate_position(balance: float, risk_percent: float, stop_loss: float):
    risk_amount = balance * (risk_percent / 100)

    if stop_loss == 0:
        return 0

    position_size = risk_amount / stop_loss
    return round(position_size, 2)

