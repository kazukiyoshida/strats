import asyncio
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
        ["python", "tests/e2e/02_stream_monitor/stream_monitor.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # wait the application is running
    time.sleep(1)

    if proc.poll() is not None:
        stdout, stderr = proc.communicate()
        print("[STDOUT]", stdout.decode(), file=sys.stderr)
        print("[STDERR]", stderr.decode(), file=sys.stderr)
        raise RuntimeError("Application process exited early")

    yield proc

    proc.terminate()
    proc.wait()


@pytest.mark.asyncio
async def test_stream_monitor(app_process):
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

    await asyncio.sleep(1)

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
