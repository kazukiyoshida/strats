import logging

from fastapi import APIRouter, Depends, Response
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
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@router.get("/strategy", tags=["strategy"])
def get_strategy(kernel: Kernel = Depends(get_kernel)):
    return response_strategy_info(kernel)


@router.post("/strategy/start", tags=["strategy"])
async def start_strategy(kernel: Kernel = Depends(get_kernel)):
    await kernel.start_strategy()
    return response_strategy_info(kernel)


@router.post("/strategy/stop", tags=["strategy"])
async def stop_strategy(kernel: Kernel = Depends(get_kernel)):
    await kernel.stop_strategy()
    return response_strategy_info(kernel)


@router.get("/monitors", tags=["monitors"])
def get_monitors(kernel: Kernel = Depends(get_kernel)):
    return response_monitors_info(kernel)


@router.post("/monitors/start", tags=["monitors"])
async def start_monitors(kernel: Kernel = Depends(get_kernel)):
    await kernel.start_monitors()
    return response_monitors_info(kernel)


@router.post("/monitors/stop", tags=["monitors"])
async def stop_monitors(kernel: Kernel = Depends(get_kernel)):
    await kernel.stop_monitors()
    return response_monitors_info(kernel)


def response_strategy_info(kernel):
    return {
        "is_alive": (kernel.strategy_task is not None and not kernel.strategy_task.done()),
    }


def response_monitors_info(kernel):
    return {
        monitor.name: {
            "is_alive": (
                monitor.name in kernel.monitor_tasks
                and not kernel.monitor_tasks[monitor.name].done()
            )
        }
        for monitor in kernel.monitors
    }
