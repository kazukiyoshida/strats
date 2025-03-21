import logging

from flask import Blueprint, current_app, jsonify
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from strats.core.kernel import Kernel

logger = logging.getLogger(__name__)
router = Blueprint("router", __name__)


def get_kernel() -> Kernel:
    kernel = current_app.config["kernel"]
    if kernel is None:
        raise Exception("kernel was not found in the Strats")
    return kernel


@router.route("/healthz", methods=["GET"])
def healthz():
    return "ok"


@router.route("/metrics", methods=["GET"])
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@router.route("/monitors", methods=["GET"])
def get_monitors():
    kernel = get_kernel()
    return jsonify(response_monitors_info(kernel))


@router.route("/monitors/start", methods=["POST"])
def start_monitors():
    kernel = get_kernel()
    kernel.start_monitors()
    return jsonify(response_monitors_info(kernel))


@router.route("/monitors/stop", methods=["POST"])
def stop_monitors():
    kernel = get_kernel()
    kernel.stop_monitors()
    return jsonify(response_monitors_info(kernel))


def response_monitors_info(kernel):
    return {
        name: {
            "is_alive": monitor_thread.is_alive(),
        }
        for name, monitor_thread in kernel.monitor_threads.items()
    }
