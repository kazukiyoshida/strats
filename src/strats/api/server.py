import logging
from logging.config import dictConfig

import uvicorn
from fastapi import FastAPI

from strats.core.kernel import Kernel
from strats.util.log_config import LOGGING_CONFIG

from .router import get_kernel, router

BANNER = r"""
 _______ _______  ______ _______ _______ _______
 |______    |    |_____/ |_____|    |    |______
 ______|    |    |     \ |     |    |    ______|
"""


def create_get_kernel(kernel):
    def get_kernel():
        return kernel

    return get_kernel


class Strats(Kernel):
    def serve(self, host="0.0.0.0", port=8000):
        dictConfig(LOGGING_CONFIG)
        logger = logging.getLogger(__name__)

        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_kernel] = create_get_kernel(self)
        logger.info(BANNER)

        # Use lower-level uvicorn API to handle SIGINT/SIGTERM properly
        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            log_config=LOGGING_CONFIG,
        )
        server = uvicorn.Server(config)
        try:
            server.run()
        except KeyboardInterrupt:
            pass
