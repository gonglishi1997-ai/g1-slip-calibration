"""Summarise a simulation log: joint tracking error, marker visibility, and detection accuracy."""
import json
import sys

import numpy as np
from scipy.optimize import linear_sum_assignment

log = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "g1_sim_log.json"))
GATE = 5.0  # px: a detection farther than this from every projected marker counts as unmatched

# 1) Joint tracking: commanded (recording) vs simulated joint angle.
for side in ("left", "right"):
    err = np.degrees(np.abs(np.array(log["sim"][side]) - np.array(log["cmd"][side])))
    print(f"{side} arm tracking error  mean {err.mean():.2f} deg   P95 {np.percentile(err, 95):.2f} deg"
          f"   max {err.max():.2f} deg")

# 2) Detection vs projected truth, frame by frame (Hungarian matching with a gate).
errors, n_det, n_match, n_inview = [], 0, 0, 0
missing_per_frame = []
for truth, det in zip(log["truth_px"], log["detected"]):
    truth, det = np.array(truth), np.array(det).reshape(-1, 2)
    inview = (truth[:, 0] >= 0) & (truth[:, 0] < 640) & (truth[:, 1] >= 0) & (truth[:, 1] < 480)
    n_inview += inview.sum()
    n_det += len(det)
    matched = 0
    if len(det):
        d = np.linalg.norm(truth[:, None, :] - det[None, :, :], axis=2)
        r, c = linear_sum_assignment(d)
        ok = d[r, c] < GATE
        errors.extend(d[r, c][ok])
        matched = ok.sum()
    n_match += matched
    missing_per_frame.append(12 - matched)

errors = np.array(errors)
missing = np.array(missing_per_frame)
frames = len(log["t"])
print(f"frames {frames}, markers in view {n_inview}/{12 * frames}")
print(f"detected blobs {n_det}, matched to a marker {n_match} ({n_match / (12 * frames):.1%} of all markers)")
print(f"detection error: mean {errors.mean():.2f} px   P95 {np.percentile(errors, 95):.2f} px   max {errors.max():.2f} px")
print(f"frames with all 12 markers visible: {(missing == 0).mean():.1%};"
      f" with >=1 marker missing: {(missing > 0).mean():.1%}; worst frame missing {missing.max()}")
print(f"unmatched detections (merged / partial blobs): {n_det - n_match}")
