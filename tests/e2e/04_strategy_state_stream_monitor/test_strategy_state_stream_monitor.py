import asyncio
import queue
import re
import subprocess
import sys
import threading
import time
from urllib.parse import urljoin

import pytest
import requests

BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="function")
def app_process():
    proc = subprocess.Popen(
        ["python", "tests/e2e/04_strategy_state_stream_monitor/strategy_state_stream_monitor.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
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
    expect = {"is_configured": True, "is_running": False}
    assert res.status_code == 200
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

    # >> run

    res = requests.post(urljoin(BASE_URL, "/strategy/start"))
    expect = {"is_configured": True, "is_running": True}
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

    # >> check

    res = requests.get(urljoin(BASE_URL, "/metrics"))
    assert res.status_code == 200
    assert extract_unlabeled_metric_value(res.text, "prices_prices_bid") == 100.0
    assert extract_unlabeled_metric_value(res.text, "prices_prices_ask") == 101.0
    assert extract_unlabeled_metric_value(res.text, "prices_prices_spread") == 1.0
    assert extract_unlabeled_metric_value(res.text, "prices_prices_update_count_total") == 1.0

    stderrs = get_stderr_list(app_process)
    # the last stdout is "GET /metrics HTTP/1.1 200 OK"
    assert "INFO : __main__ : strategy > bid: 100" in stderrs[-2]

    # >> stop

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

    res = requests.post(urljoin(BASE_URL, "/strategy/stop"))
    expect = {"is_configured": True, "is_running": False}
    assert res.status_code == 200
    assert res.json() == expect


def extract_unlabeled_metric_value(body: str, metric_name: str) -> float:
    pattern = rf"^{re.escape(metric_name)} ([0-9.e+-]+)"
    match = re.search(pattern, body, re.MULTILINE)
    if not match:
        raise ValueError(f"Metric {metric_name} not found")
    return float(match.group(1))


def read_stderr_lines(process, output_queue):
    for line in process.stderr:
        output_queue.put(line)
    output_queue.put(None)  # signal end of stream


def get_stderr_list(process, timeout=1) -> list[str]:
    stderrs = []

    q: queue.Queue = queue.Queue()
    t = threading.Thread(target=read_stderr_lines, args=(process, q), daemon=True)
    t.start()

    start_time = time.time()
    while True:
        try:
            line = q.get(timeout=0.1)
            if line is None:  # end of stream
                break
            stderrs.append(line.strip())
        except queue.Empty:
            if time.time() - start_time > timeout:
                break
    return stderrs
