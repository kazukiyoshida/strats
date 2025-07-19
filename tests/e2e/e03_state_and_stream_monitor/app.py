import asyncio
from collections.abc import AsyncGenerator
from decimal import Decimal

from strats import Data, State, Strats
from strats.model import (
    PricesData,
    PricesMetrics,
    prices_data_to_prices_metrics,
)
from strats.monitor import StreamClient, StreamMonitor


def _id(p: PricesData, _) -> PricesData:
    return p


class TestStreamClient(StreamClient):
    def prepare(self, name: str):
        self.name = name

    async def stream(self) -> AsyncGenerator[PricesData]:
        for i in range(10):
            yield PricesData(
                bid=Decimal("100") + Decimal(i),
                ask=Decimal("101") + Decimal(i),
            )
            await asyncio.sleep(10)


class TestState(State):
    prices = Data(
        data_class=PricesData,
        metrics_class=PricesMetrics,
        source_to_data=_id,
        data_to_metrics=prices_data_to_prices_metrics,
    )


def main():
    stream_monitor = StreamMonitor(
        monitor_name="stream_monitor",
        data_name="prices",
        client=TestStreamClient(),
    )
    state = TestState()
    Strats(
        state=state,
        monitors=[stream_monitor],
    ).serve()


if __name__ == "__main__":
    main()
