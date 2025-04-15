import asyncio
import logging
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Optional, Protocol

from strats.exchange import StreamClient

logger = logging.getLogger(__name__)


class HandlerFunction(Protocol):
    def __call__(self, s: str) -> datetime:
        pass


def default_event_handler(s: str) -> datetime:
    return datetime.strptime(s.strip(), "%Y-%m-%d %H:%M:%S")


class ClockStreamClient(StreamClient):
    def __init__(
        self,
        *,
        socket_path: str,
        event_handler: Optional[HandlerFunction] = None,
    ):
        self.socket_path = socket_path
        if event_handler is None:
            self.event_handler = default_event_handler
        else:
            self.event_handler = event_handler

    async def stream(self) -> AsyncGenerator[datetime]:
        try:
            reader, writer = await asyncio.open_unix_connection(self.socket_path)
            logger.info("connected to clock server")

            while True:
                data = await reader.readline()

                if not data:
                    logger.info("EOF received from server.")
                    break

                try:
                    msg = data.decode()
                except Exception as e:
                    logger.error(f"failed to parse timestamp: {e}")
                    continue

                yield self.event_handler(msg)

        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Unhandled exception in ClockStreamClient: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            logger.info("ClockStreamClient stopped")
