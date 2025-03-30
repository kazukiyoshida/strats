from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from prometheus_client import Counter, Gauge


@dataclass
class PricesData:
    bid: Optional[Decimal] = field(default=None)
    ask: Optional[Decimal] = field(default=None)


class PricesMetrics:
    def __init__(self, prefix: Optional[str] = None):
        s = "" if prefix is None else f"{prefix}_"
        self.bid = Gauge(f"{s}prices_bid", "")
        self.ask = Gauge(f"{s}prices_ask", "")
        self.spread = Gauge(f"{s}prices_spread", "")
        self.update_count = Counter(f"{s}prices_update_count", "")

    def default_data_mapper(self, d: PricesData):
        if d.bid is not None and d.ask is not None:
            self.bid.set(float(d.bid))
            self.ask.set(float(d.ask))
            self.spread.set(float(d.ask - d.bid))
            self.update_count.inc()
