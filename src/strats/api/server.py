import logging

import uvicorn
from fastapi import FastAPI

from strats.core.kernel import Kernel

from .router import get_kernel, router

BANNER = r"""
 _______ _______  ______ _______ _______ _______
 |______    |    |_____/ |_____|    |    |______
 ______|    |    |     \ |     |    |    ______|
"""

logger = logging.getLogger(__name__)


def create_get_kernel(kernel):
    def get_kernel():
        return kernel

    return get_kernel


class Strats(Kernel):
    def serve(self, host="0.0.0.0", port=8000):
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_kernel] = create_get_kernel(self)
        logger.info(BANNER)
        uvicorn.run(app=app)
