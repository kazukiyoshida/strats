import asyncio
from collections.abc import AsyncGenerator
from decimal import Decimal

from strats import Data, State, Strats
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
    async def stream(self) -> AsyncGenerator[PricesData]:
        try:
            for i in range(10):
                yield PricesData(
                    bid=Decimal("100") + Decimal(i),
                    ask=Decimal("101") + Decimal(i),
                )
                await asyncio.sleep(10)
        except asyncio.CancelledError:
            raise
        except Exception:
            pass


class TestState(State):
    prices = Data(
        source_class=PricesData,
        data_class=PricesData,
        metrics_class=PricesMetrics,
        source_to_data=_id,
        data_to_metrics=prices_data_to_prices_metrics,
    )


def main():
    stream_monitor = StreamMonitor(
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
