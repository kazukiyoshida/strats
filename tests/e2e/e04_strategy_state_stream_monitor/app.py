import asyncio
import logging
from collections.abc import AsyncGenerator
from decimal import Decimal

from strats import Data, State, Strategy, Strats
from strats.model import (
    PricesData,
    PricesMetrics,
    prices_data_to_prices_metrics,
)
from strats.monitor import StreamClient, StreamMonitor

logger = logging.getLogger(__name__)


class SampleState(State):
    prices = Data(
        data=PricesData(),
        metrics=PricesMetrics(),
        data_to_metrics=prices_data_to_prices_metrics,
    )


class SampleStreamClient(StreamClient):
    async def stream(self) -> AsyncGenerator[PricesData]:
        for i in range(100):
            yield PricesData(
                bid=Decimal("100") + Decimal(i),
                ask=Decimal("101") + Decimal(i),
            )
            await asyncio.sleep(5)


class SampleStrategy(Strategy):
    async def run(self, clock, state):
        while True:
            item = await state.queue.get()
            logger.info(f"strategy > bid: {item.source.bid}")


def main():
    Strats(
        state=SampleState(),
        strategy=SampleStrategy(),
        monitors=[
            StreamMonitor(
                data_name="prices",
                client=SampleStreamClient(),
            ),
        ],
    ).serve()


if __name__ == "__main__":
    main()
