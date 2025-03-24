import argparse
import asyncio
import logging
import sys
from dataclasses import dataclass

import strats_oanda
from strats_oanda.client import PricingStreamClient, TransactionClient
from strats_oanda.converter import client_price_to_prices
from strats_oanda.model import ClientPrice

from strats import DataWithMetrics, Strats
from strats.model import PricesData, PricesMetrics
from strats.monitor import StreamMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default="local", help="local|practice|prod")
    opts = parser.parse_args(argv)
    return opts


@dataclass
class State:
    prices: DataWithMetrics[PricesData, PricesMetrics]

    def update_prices(self, msg: ClientPrice):
        data = client_price_to_prices(msg)
        if data is not None:
            self.prices.data = data


class Strategy:
    def __init__(self):
        pass

    async def run(self, stop_event: asyncio.Event):
        while not stop_event.is_set():
            await asyncio.sleep(2)
            print("strategy..")


def main(argv=sys.argv[1:]):
    opts = parse_args(argv)

    if opts.env == "prod":
        file_path = ".strats_oanda_prod.yaml"
    elif opts.env == "practice":
        file_path = ".strats_oanda_practice.yaml"
    else:
        file_path = ".strats_oanda.yaml"

    logger.info(f"use {file_path}")
    strats_oanda.basic_config(use_file=True, file_path=file_path)

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

    transaction_monitor = StreamMonitor[State, ClientPrice](
        state=state,
        client=TransactionClient(),
        handler=lambda state, msg: print(msg),
    )

    strategy = Strategy()

    Strats(
        state=state,
        strategy=strategy,
        monitors={
            "prices_monitor": prices_monitor,
            "transaction_monitor": transaction_monitor,
        },
    ).serve()


if __name__ == "__main__":
    main()
