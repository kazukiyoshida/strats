import asyncio
import re
from urllib.parse import urljoin

import pytest
import requests

BASE_URL = "http://localhost:8000"
APPLICATION_FILEPATH = "tests/e2e/e03_state_and_stream_monitor/app.py"


@pytest.mark.asyncio
async def test_state_and_stream_monitor(app_process_factory):
    proc = app_process_factory(APPLICATION_FILEPATH)

    try:
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
                "StreamMonitor_1": {
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
                "StreamMonitor_1": {
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
                "StreamMonitor_1": {
                    "is_running": False,
                },
            },
        }
        assert res.status_code == 200
        assert res.json() == expect

    finally:
        proc.terminate()
        proc.wait()


def extract_unlabeled_metric_value(body: str, metric_name: str) -> float:
    pattern = rf"^{re.escape(metric_name)} ([0-9.e+-]+)"
    match = re.search(pattern, body, re.MULTILINE)
    if not match:
        raise ValueError(f"Metric {metric_name} not found")
    return float(match.group(1))
