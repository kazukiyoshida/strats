from dataclasses import dataclass
from decimal import Decimal

from prometheus_client import Counter, Gauge


@dataclass
class PricesData:
    bid: Decimal = Decimal("0")
    ask: Decimal = Decimal("0")


class PricesMetrics:
    def __init__(self, prefix: str):
        self.bid = Gauge(f"{prefix}_prices_bid", "")
        self.ask = Gauge(f"{prefix}_prices_ask", "")
        self.spread = Gauge(f"{prefix}_prices_spread", "")
        self.update_count = Counter(f"{prefix}_prices_update_count", "")


def prices_data_to_prices_metrics(data: PricesData, metrics: PricesMetrics):
    metrics.bid.set(float(data.bid))
    metrics.ask.set(float(data.ask))
    metrics.spread.set(float(data.ask - data.bid))
    metrics.update_count.inc()
