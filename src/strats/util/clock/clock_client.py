import asyncio
import logging
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from strats.monitor import StreamClient

from .clock_server import DATETIME_FORMAT, SOCKET_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClockClient(StreamClient):
    def __init__(
        self,
        tz: Optional[ZoneInfo] = None,
        mock: bool = False,
        mock_socket_path: str = SOCKET_PATH,
        mock_datetime_format: str = DATETIME_FORMAT,
    ):
        self.tz = tz
        self.mock = mock
        self.mock_socket_path = mock_socket_path
        self.mock_datetime_format = mock_datetime_format
        self.mock_datetime: Optional[datetime] = None

    @property
    def datetime(self):
        if not self.mock:
            return datetime.now(self.tz)

        if self.mock_datetime is None:
            raise ValueError("Clock is not running yet")
        return self.mock_datetime

    @property
    def ohlc_datetime(self):
        return self.datetime.replace(second=0, microsecond=0)

    def prepare(self, name: str):
        self.name = name

    async def stream(self):
        if not self.mock:
            return

        # Open async Unix‐domain socket connection
        reader, writer = await asyncio.open_unix_connection(path=self.mock_socket_path)
        logger.info("connected to clock server")

        try:
            while True:
                # Read up to 1024 bytes; returns b'' on EOF
                data = await reader.read(1024)
                if not data:
                    break

                text = data.decode().strip()
                timestamp = datetime.strptime(text, self.mock_datetime_format)
                self.mock_datetime = timestamp.replace(tzinfo=self.tz)
                yield self.mock_datetime

        except asyncio.CancelledError:
            # Allow clean cancellation
            logger.info("stream task cancelled")
            raise

        finally:
            writer.close()
            await writer.wait_closed()
            logger.info("clock server disconnected")
