import asyncio
from urllib.parse import urljoin

import pytest
import requests

BASE_URL = "http://localhost:8000"
APPLICATION_FILEPATH = "tests/e2e/e02_stream_monitor_negative/app.py"


@pytest.mark.asyncio
async def test_app(app_process_factory):
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

        # As soon as the monitor starts, an error occurs and it automatically
        # transitions to the STOPPED state
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

        # If you run stop on a monitor that is already in the STOPPED state, it still succeeds.
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
