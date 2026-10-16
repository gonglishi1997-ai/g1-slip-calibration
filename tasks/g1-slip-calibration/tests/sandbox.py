"""Run the submitted program as an unprivileged user and write the CTRF test report."""

import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

APP_DIR = Path(os.environ.get("APP_DIR", "/app"))
NOBODY = 65534


def execute(program, input_dir, output_json, timeout):
    """Run `python program INPUT OUTPUT` as nobody, single-threaded, and kill its process group on exit."""
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
    with tempfile.TemporaryFile(mode="w+") as out, tempfile.TemporaryFile(mode="w+") as err:
        proc = subprocess.Popen(
            [sys.executable, str(program), str(input_dir), str(output_json)],
            stdout=out,
            stderr=err,
            text=True,
            cwd=APP_DIR,
            user=NOBODY,
            group=NOBODY,
            start_new_session=True,
            env=env,
        )
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
            raise
        finally:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        out.seek(0)
        err.seek(0)
        return subprocess.CompletedProcess(proc.args, proc.returncode, out.read(), err.read())


def write_ctrf(tests, start, path):
    passed = sum(t["status"] == "passed" for t in tests)
    report = {
        "results": {
            "tool": {"name": "g1-slip-calibration-verifier"},
            "summary": {
                "tests": len(tests),
                "passed": passed,
                "failed": len(tests) - passed,
                "skipped": 0,
                "pending": 0,
                "other": 0,
                "start": int(start * 1000),
                "stop": int(time.time() * 1000),
            },
            "tests": tests,
        }
    }
    Path(path).write_text(json.dumps(report, indent=2) + "\n")
