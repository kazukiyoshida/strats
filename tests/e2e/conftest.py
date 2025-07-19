import subprocess
import sys
import time

import pytest


@pytest.fixture(scope="function")
def app_process_factory():
    # The argument is application filepath
    def _start(filepath: str):
        proc = subprocess.Popen(
            ["python", filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        time.sleep(0.5)

        if proc.poll() is not None:
            stdout, stderr = proc.communicate()
            print("[STDOUT]", stdout.encode(), file=sys.stderr)
            print("[STDERR]", stderr.encode(), file=sys.stderr)
            raise RuntimeError("Application process exited early")

        return proc

    yield _start
