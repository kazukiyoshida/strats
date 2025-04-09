import asyncio
import re
import subprocess
import sys
import time
from urllib.parse import urljoin

import pytest
import requests

BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="function")
def app_process():
    proc = subprocess.Popen(
        ["python", "tests/e2e/03_state_and_stream_monitor/state_and_stream_monitor.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # wait the application is running
    time.sleep(0.5)

    if proc.poll() is not None:
        stdout, stderr = proc.communicate()
        print("[STDOUT]", stdout.decode(), file=sys.stderr)
        print("[STDERR]", stderr.decode(), file=sys.stderr)
        raise RuntimeError("Application process exited early")

    yield proc

    proc.terminate()
    proc.wait()


@pytest.mark.asyncio
async def test_state_and_stream_monitor(app_process):
    # >> healthz, metrics

    res = requests.get(urljoin(BASE_URL, "/healthz"))
    assert res.status_code == 200
    assert res.json() == "ok"

    res = requests.get(urljoin(BASE_URL, "/metrics"))
    assert res.status_code == 200

    # >> strategy

    res = requests.get(urljoin(BASE_URL, "/strategy"))
    expect = {"is_configured": False, "is_running": False}
    assert res.status_code == 200
    assert res.json() == expect

    res = requests.post(urljoin(BASE_URL, "/strategy/start"))
    expect = {"detail": "Missing strategy configuration"}
    assert res.status_code == 400
    assert res.json() == expect

    res = requests.post(urljoin(BASE_URL, "/strategy/stop"))
    expect = {"detail": "Missing strategy configuration"}
    assert res.status_code == 400
    assert res.json() == expect

    # >> monitors

    res = requests.get(urljoin(BASE_URL, "/monitors"))
    expect = {
        "is_configured": True,
        "monitors": {
            "stream_monitor": {
                "is_running": False,
            },
        },
    }
    assert res.status_code == 200
    assert res.json() == expect

    res = requests.post(urljoin(BASE_URL, "/monitors/start"))
    expect = {
        "is_configured": True,
        "monitors": {
            "stream_monitor": {
                "is_running": True,
            },
        },
    }
    assert res.status_code == 200
    assert res.json() == expect

    await asyncio.sleep(0.5)

    res = requests.get(urljoin(BASE_URL, "/metrics"))
    assert res.status_code == 200
    assert extract_unlabeled_metric_value(res.text, "prices_prices_bid") == 100.0
    assert extract_unlabeled_metric_value(res.text, "prices_prices_ask") == 101.0
    assert extract_unlabeled_metric_value(res.text, "prices_prices_spread") == 1.0
    assert extract_unlabeled_metric_value(res.text, "prices_prices_update_count_total") == 1.0

    res = requests.post(urljoin(BASE_URL, "/monitors/stop"))
    expect = {
        "is_configured": True,
        "monitors": {
            "stream_monitor": {
                "is_running": False,
            },
        },
    }
    assert res.status_code == 200
    assert res.json() == expect


def extract_unlabeled_metric_value(body: str, metric_name: str) -> float:
    pattern = rf"^{re.escape(metric_name)} ([0-9.e+-]+)"
    match = re.search(pattern, body, re.MULTILINE)
    if not match:
        raise ValueError(f"Metric {metric_name} not found")
    return float(match.group(1))
