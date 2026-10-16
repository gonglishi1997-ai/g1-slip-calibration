"""Regenerate every public and hidden campaign of the task from the bundled joint-state recordings.

    python generator/build.py OUTPUT_DIR

Two stages, both deterministic given the seeds below:

1. base_campaigns.py builds three-record campaigns from real G1 joint states: a shared rig
   (mounts, encoder offsets, camera pose and intrinsics), per-record clocks, occlusion,
   frame loss, separated outliers, and labelled ground truth.
2. faults.py adds an unmarked mount slip in two of the three records, a coherent "ghost"
   target that follows the arm with a wrong mount, pixel noise, exact retransmissions,
   and held-out probe configurations used by the verifier.

The output has the same layout as the task: environment/public/... and tests/cases/...
"""

import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from base_campaigns import campaign as build_base_campaign  # noqa: E402
from faults import create as add_faults  # noqa: E402

SOURCES = HERE / "sources"

# name, source episodes for the three records, seed, public?
BASE_CAMPAIGNS = [
    ("example_a", [0, 0, 0], 106111, True),
    ("example_b", [0, 0, 0], 106102, True),
    ("fresh_a", [1, 2, 3], 681401, False),
    ("fresh_b", [3, 1, 2], 681402, False),
]

# final name, base campaign, seed, public?, add slips?
FINAL_CAMPAIGNS = [
    ("example_a", "example_a", 61101, True, True),
    ("example_b", "example_b", 61102, True, True),
    ("held_a", "fresh_a", 61901, False, True),
    ("held_b", "fresh_b", 61902, False, True),
    ("held_no_slip", "fresh_b", 61903, False, False),  # no-slip control on the same rig as held_b
]


def subdir(public):
    return "environment/public" if public else "tests/cases"


def build(out_root):
    out_root = Path(out_root)
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        for name, episodes, seed, public in BASE_CAMPAIGNS:
            build_base_campaign(base, SOURCES, name, episodes, seed, public)
        for name, source, seed, public, slips in FINAL_CAMPAIGNS:
            sub = subdir(public)
            add_faults(base / sub / source, out_root / sub / name, seed, slips=slips)
    # Grading-only files never ship with the public examples.
    for private in (out_root / "environment/public").rglob("private.json"):
        private.unlink()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    target = Path(sys.argv[1])
    if target.exists() and any(target.iterdir()):
        raise SystemExit(f"{target} is not empty")
    build(target)
    print("written to", target)
