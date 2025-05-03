import logging
import os
import socket
import time
from datetime import datetime, timedelta

SOCKET_PATH = "/tmp/strats_unix_domain_socket"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clock_server(
    init_time: datetime,
    speed: int = 1,
    socket_path: str = SOCKET_PATH,
    datetime_format: str = DATETIME_FORMAT,
):
    if os.path.exists(socket_path):
        os.remove(socket_path)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(socket_path)
    server.listen(1)
    logger.info(f"clock server is listening on {socket_path}")

    t = init_time

    while True:
        conn, _ = server.accept()
        logger.info("client connected")
        try:
            while True:
                msg = t.strftime(datetime_format)
                conn.sendall(msg.encode() + b"\n")
                logger.info(msg)

                time.sleep(1 / speed)
                t += timedelta(seconds=1)

        except (BrokenPipeError, ConnectionResetError):
            logger.info("client disconnected")

        finally:
            conn.close()
