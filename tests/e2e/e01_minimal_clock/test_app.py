from urllib.parse import urljoin

import requests

BASE_URL = "http://localhost:8000"
APPLICATION_FILEPATH = "tests/e2e/e01_minimal_clock/app.py"


def test_minimal(app_process_factory):
    proc = app_process_factory(APPLICATION_FILEPATH)

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
    expect = {"is_configured": False}
    assert res.status_code == 200
    assert res.json() == expect

    res = requests.post(urljoin(BASE_URL, "/monitors/start"))
    expect = {"detail": "Missing monitors configuration"}
    assert res.status_code == 400
    assert res.json() == expect

    res = requests.post(urljoin(BASE_URL, "/monitors/stop"))
    expect = {"detail": "Missing monitors configuration"}
    assert res.status_code == 400
    assert res.json() == expect

    # >> clock

    res = requests.get(urljoin(BASE_URL, "/clock"))
    expect = {
        "is_real": False,
        "is_running": False,
        "datetime": "2025-01-01T12:00:00+09:00",
    }
    assert res.status_code == 200
    assert res.json() == expect

    res = requests.post(urljoin(BASE_URL, "/clock/start"))
    expect = {
        "is_real": False,
        "is_running": True,
        "datetime": "2025-01-01T12:00:00+09:00",
    }
    assert res.status_code == 200
    assert res.json() == expect

    res = requests.post(urljoin(BASE_URL, "/clock/stop"))
    expect = {"detail": "Missing monitors configuration"}
    assert res.status_code == 200
    assert not res.json()["is_running"]

    proc.terminate()
    proc.wait()
