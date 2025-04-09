import asyncio
from collections.abc import AsyncGenerator
from decimal import Decimal
from typing import Optional

from strats import Data, State, Strategy, Strats
from strats.exchange import StreamClient
from strats.model import (
    PricesData,
    PricesMetrics,
    prices_data_to_prices_metrics,
)
from strats.monitor import StreamMonitor


def _id(p: PricesData) -> PricesData:
    return p


class TestStreamClient(StreamClient):
    async def stream(self, stop_event: asyncio.Event) -> AsyncGenerator[PricesData]:
        for i in range(100):
            yield PricesData(
                bid=Decimal("100") + Decimal(i),
                ask=Decimal("101") + Decimal(i),
            )
            await asyncio.sleep(5)


class TestState(State):
    prices = Data(
        source_class=PricesData,
        data_class=PricesData,
        metrics_class=PricesMetrics,
        source_to_data=_id,
        data_to_metrics=prices_data_to_prices_metrics,
    )


class TestStrategy(Strategy):
    async def run(
        self,
        state: Optional[State],
        stop_event: asyncio.Event,
    ):
        if state is None:
            raise ValueError("state is not found")

        while not stop_event.is_set():
            try:
                item = await asyncio.wait_for(state.queue.get(), timeout=1)
                print(f"strategy > bid: {item[0].bid}")
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"got an error: {e}")
                continue


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
