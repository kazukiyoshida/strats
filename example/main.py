import argparse
import asyncio
import logging
import sys

import strats_oanda
from strats_oanda.client import PricingStreamClient
from strats_oanda.converter import client_price_to_prices_data
from strats_oanda.model import ClientPrice

from strats import Data, State, Strategy, Strats
from strats.model import (
    PricesData,
    PricesMetrics,
    prices_data_to_prices_metrics,
)
from strats.monitor import StreamMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default="local", help="local|practice|prod")
    opts = parser.parse_args(argv)
    return opts


class ExampleState(State):
    prices = Data(
        source_class=ClientPrice,
        data_class=PricesData,
        metrics_class=PricesMetrics,
        source_to_data=client_price_to_prices_data,
        data_to_metrics=prices_data_to_prices_metrics,
    )


class ExampleStrategy(Strategy):
    async def run(
        self,
        state: ExampleState,
        stop_event: asyncio.Event,
    ):
        while not stop_event.is_set():
            await asyncio.sleep(2)
            print("strategy..", state.prices)


def configure_oanda(env: str):
    if env == "prod":
        file_path = ".strats_oanda_prod.yaml"
    elif env == "practice":
        file_path = ".strats_oanda_practice.yaml"
    else:
        file_path = ".strats_oanda.yaml"

    logger.info(f"use {file_path}")
    strats_oanda.basic_config(use_file=True, file_path=file_path)


def main(argv=sys.argv[1:]):
    opts = parse_args(argv)

    configure_oanda(opts.env)

    state = ExampleState()

    prices_monitor = StreamMonitor[ExampleState](
        name="prices_monitor",
        state_data=state.prices,
        client=PricingStreamClient(instruments=["USD_JPY"]),
    )

    strategy = ExampleStrategy()

    Strats(
        state=state,
        strategy=strategy,
        monitors=[
            prices_monitor,
        ],
    ).serve()


if __name__ == "__main__":
    main()
