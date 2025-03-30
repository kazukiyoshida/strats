import argparse
import asyncio
import logging
import sys
from dataclasses import dataclass
from datetime import datetime

import strats_oanda
from strats_oanda.client import PricingStreamClient, TransactionClient
from strats_oanda.converter import client_price_to_prices
from strats_oanda.model import ClientPrice

from strats import DataWithMetrics, Strategy, Strats
from strats.exchange.backtest import ClockStreamClient
from strats.model import Clock, PricesData, PricesMetrics
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
    clock: DataWithMetrics[Clock, None]

    def update_prices(self, msg: ClientPrice):
        data = client_price_to_prices(msg)
        if data is not None:
            self.prices.data = data

    def update_clock(self, t: datetime):
        self.clock.data = t


class Strategy(Strategy):
    async def run(
        self,
        state: State,
        stop_event: asyncio.Event,
    ):
        while not stop_event.is_set():
            await asyncio.sleep(2)
            print("strategy..", state.prices.data)


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
            data=PricesData(),
            metrics=PricesMetrics(prefix="usdjpy"),
        ),
        clock=Clock(),
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

    clock_monitor = StreamMonitor[State, datetime](
        state=state,
        client=ClockStreamClient(socket_path="/tmp/shaft_unix_domain_socket"),
        handler=lambda state, msg: print(msg),
    )

    strategy = Strategy()

    Strats(
        state=state,
        strategy=strategy,
        monitors={
            "prices_monitor": prices_monitor,
            "transaction_monitor": transaction_monitor,
            "clock_monitor": clock_monitor,
        },
    ).serve()


if __name__ == "__main__":
    main()
