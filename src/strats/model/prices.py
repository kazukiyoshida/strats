from dataclasses import dataclass
from typing import Optional

from prometheus_client import Gauge


@dataclass
class PricesData:
    bid: float
    ask: float


class PricesMetrics:
    def __init__(self, prefix: Optional[str] = None):
        s = "" if prefix is None else f"{prefix}_"
        self.bid = Gauge(f"{s}prices_bid", "")
        self.ask = Gauge(f"{s}prices_ask", "")
        self.spread = Gauge(f"{s}prices_spread", "")


def prices_mapper(d: PricesData, m: PricesMetrics):
    m.bid.set(d.bid)
    m.ask.set(d.ask)
    m.spread.set(d.ask - d.bid)
