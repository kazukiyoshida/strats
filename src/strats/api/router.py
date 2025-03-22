import logging

from fastapi import APIRouter, Depends
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from strats.core.kernel import Kernel

logger = logging.getLogger(__name__)

router = APIRouter()


def get_kernel() -> Kernel:
    raise NotImplementedError("get_kernel is not yet bound")


@router.get("/healthz")
def healthz():
    return "ok"


@router.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@router.get("/monitors")
def get_monitors(kernel: Kernel = Depends(get_kernel)):
    return response_monitors_info(kernel)


@router.post("/monitors/start")
def start_monitors(kernel: Kernel = Depends(get_kernel)):
    kernel.start_monitors()
    return response_monitors_info(kernel)


@router.post("/monitors/stop")
def stop_monitors(kernel: Kernel = Depends(get_kernel)):
    kernel.stop_monitors()
    return response_monitors_info(kernel)


def response_monitors_info(kernel):
    return {
        name: {
            "is_alive": monitor_thread.is_alive(),
        }
        for name, monitor_thread in kernel.monitor_threads.items()
    }
