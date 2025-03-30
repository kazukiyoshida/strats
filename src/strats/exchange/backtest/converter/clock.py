from datetime import datetime

from strats.model import Clock


def client_price_to_prices(t: datetime) -> Clock:
    return Clock(t=t)
