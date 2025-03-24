from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from prometheus_client import Gauge


@dataclass
class PricesData:
    bid: Decimal
    ask: Decimal


class PricesMetrics:
    def __init__(self, prefix: Optional[str] = None):
        s = "" if prefix is None else f"{prefix}_"
        self.bid = Gauge(f"{s}prices_bid", "")
        self.ask = Gauge(f"{s}prices_ask", "")
        self.spread = Gauge(f"{s}prices_spread", "")

    def default_data_mapper(self, d: PricesData):
        self.bid.set(float(d.bid))
        self.ask.set(float(d.ask))
        self.spread.set(float(d.ask - d.bid))
