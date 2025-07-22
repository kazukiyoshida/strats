from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from prometheus_client import Counter, Gauge


@dataclass
class PricesData:
    bid: Decimal = Decimal("0")
    ask: Decimal = Decimal("0")


class PricesMetrics:
    def __init__(self, prefix: Optional[str] = None):
        p = "" if prefix is None else f"{prefix}_"
        self.bid = Gauge(p + "prices_bid", "")
        self.ask = Gauge(p + "prices_ask", "")
        self.spread = Gauge(p + "prices_spread", "")
        self.update_count = Counter(p + "prices_update_count", "")


def prices_data_to_prices_metrics(data: PricesData, metrics: PricesMetrics):
    metrics.bid.set(float(data.bid))
    metrics.ask.set(float(data.ask))
    metrics.spread.set(float(data.ask - data.bid))
    metrics.update_count.inc()
