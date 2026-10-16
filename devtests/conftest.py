import sys
from pathlib import Path

TASK = Path(__file__).resolve().parents[1] / "tasks" / "g1-slip-calibration"
sys.path.insert(0, str(TASK / "tests"))  # grading.py, check.py
sys.path.insert(0, str(TASK / "environment"))  # camera_model.py, kinematics.py
