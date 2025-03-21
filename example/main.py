import logging

from strats_oanda.client import PricingStreamClient

from strats import Strats
from strats.core import DataWithMetrics, singletondataclass
from strats.model import PricesData, PricesMetrics, prices_mapper
from strats.monitor import StreamMonitor

logging.basicConfig(level=logging.INFO)


@singletondataclass
class State:
    prices: DataWithMetrics[PricesData, PricesMetrics]


prices = DataWithMetrics(
    data=PricesData(
        bid=0,
        ask=0,
    ),
    metrics=PricesMetrics(prefix="usdjpy"),
    mapper=prices_mapper,
)

state = State(
    prices=prices,
)

prices_monitor = StreamMonitor(
    state=state,
    client=PricingStreamClient(instruments=["USD_JPY"]),
    handler=None,
)

app = Strats(
    state=state,
    monitors={
        "prices_monitor": prices_monitor,
    },
)

app.serve()
