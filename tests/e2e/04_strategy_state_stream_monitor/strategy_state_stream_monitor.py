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


def _id(p: PricesData, _) -> PricesData:
    return p


class TestStreamClient(StreamClient):
    def prepare(self, name: str):
        self.name = name

    async def stream(self) -> AsyncGenerator[PricesData]:
        for i in range(100):
            yield PricesData(
                bid=Decimal("100") + Decimal(i),
                ask=Decimal("101") + Decimal(i),
            )
            await asyncio.sleep(5)


class TestState(State):
    prices = Data(
        data_class=PricesData,
        metrics_class=PricesMetrics,
        source_to_data=_id,
        data_to_metrics=prices_data_to_prices_metrics,
    )


class TestStrategy(Strategy):
    async def run(self):
        while True:
            item = await self.state.queue.get()
            logger.info(f"strategy > bid: {item.source.bid}")


def main():
    stream_monitor = StreamMonitor(
        monitor_name="stream_monitor",
        data_name="prices",
        client=TestStreamClient(),
    )
    state = TestState()
    strategy = TestStrategy()
    Strats(
        state=state,
        strategy=strategy,
        monitors=[stream_monitor],
    ).serve()


if __name__ == "__main__":
    main()
