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

    async def stream(self, stop_event: asyncio.Event) -> AsyncGenerator[datetime]:
        try:
            reader, writer = await asyncio.open_unix_connection(self.socket_path)
            logger.info("connected to clock server")

            while not stop_event.is_set():
                read_task = asyncio.create_task(reader.readline())
                stop_task = asyncio.create_task(stop_event.wait())

                done, pending = await asyncio.wait(
                    [read_task, stop_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )

                for task in pending:
                    task.cancel()

                if stop_task in done:
                    break

                if read_task in done:
                    try:
                        data = read_task.result()
                    except (asyncio.CancelledError, Exception) as e:
                        logger.error(f"read error or cancelled: {e}")
                        break

                    if not data:
                        logger.info("EOF received from server.")
                        break

                    try:
                        yield self.event_handler(data.decode())
                    except Exception as e:
                        logger.error(f"failed to parse timestamp: {e}")
                        continue

        except Exception as e:
            logger.error(f"Client error: {e}")

        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
            logger.info("client disconnected.")
