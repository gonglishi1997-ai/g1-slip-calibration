"""The reference solver must reject every corrupted input quickly and leave no output file."""

import json
import shutil
import subprocess
import sys

import pytest

from check import MALFORMED, corrupt, stage_inputs
from conftest import TASK


@pytest.mark.parametrize("mode", MALFORMED)
def test_reference_rejects(mode, tmp_path):
    case = sorted(p for p in (TASK / "tests" / "cases").iterdir() if p.is_dir())[0]
    inp, out = stage_inputs(case, tmp_path)
    last = json.loads((inp / "campaign.json").read_text())["records"][-1]
    cam = inp / last / "camera.bin"
    cam.write_bytes(corrupt(cam.read_bytes(), mode))
    app = tmp_path / "app"
    app.mkdir()
    for f in ("camera_model.py", "kinematics.py"):
        shutil.copy(TASK / "environment" / f, app / f)
    shutil.copy(TASK / "solution" / "calibrate.py", app / "calibrate.py")
    out.write_text("stale")
    run = subprocess.run(
        [sys.executable, str(app / "calibrate.py"), str(inp), str(out)],
        cwd=app,
        capture_output=True,
        timeout=15,
    )
    assert run.returncode != 0 and not out.exists()
