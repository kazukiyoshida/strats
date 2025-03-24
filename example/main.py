import logging

import strats_oanda
from strats_oanda.client import PricingStreamClient
from strats_oanda.converter import client_price_to_prices
from strats_oanda.model import ClientPrice

from strats import Strats
from strats.core import DataWithMetrics, singletondataclass
from strats.model import PricesData, PricesMetrics
from strats.monitor import StreamMonitor

logging.basicConfig(level=logging.INFO)

strats_oanda.basic_config(use_file=True, file_path=".strats_oanda.yaml")


@singletondataclass
class State:
    prices: DataWithMetrics[PricesData, PricesMetrics]

    def update_prices(self, msg: ClientPrice):
        data = client_price_to_prices(msg)
        if data is not None:
            self.prices.data = data


state = State(
    prices=DataWithMetrics(
        data=PricesData(
            bid=0,
            ask=0,
        ),
        metrics=PricesMetrics(prefix="usdjpy"),
    ),
)

prices_monitor = StreamMonitor[State, ClientPrice](
    state=state,
    client=PricingStreamClient(instruments=["USD_JPY"]),
    handler=lambda state, msg: state.update_prices(msg),
)

Strats(
    state=state,
    monitors={
        "prices_monitor": prices_monitor,
    },
).serve()
