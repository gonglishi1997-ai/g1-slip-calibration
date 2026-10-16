# g1-slip-calibration

Category: Hardware / Robotics. Deliverable: `/app/calibrate.py`, a command-line program that writes a calibration JSON for a campaign of recordings. The forward model is defined by the supplied `kinematics.py` and `camera_model.py`, not by manufacturer geometry.

## Why it is hard

The detections carry no marker identities and no track IDs. A wrong clock picks the wrong joint angles for an image; a wrong marker assignment can produce a mount estimate that looks locally convincing. Occlusion shows different marker subsets in different recordings, so no single recording identifies the rig. A real mount slip has to be told apart from a clock error and from a ghost target that follows the same arm motion. The solver has to reconcile these discrete choices with continuous geometry across records, which needs a good initialisation; more optimiser iterations alone do not help.

The situation is realistic: a calibration engineer sees it when an optical target moves during a multi-session robot calibration.

## Reference solution

`solution/calibrate.py` starts from two initial calibrations (track-based on the full records, and a single-record solver on the first 36 % of each record, which is before any slip). From each, it alternates one-to-one identity assignment with robust least squares, detects a possible slip per record, and keeps a piecewise-mount model only if it beats a constant mount after full refinement. Records that show only one arm borrow the shared parameters from the others. The program reads only its input directory.

## Verification

Three hidden campaigns of three records each, one of them without any slip, plus five corrupted-input cases. Geometry is checked on held-out joint configurations and at the true detection times rather than by parameter equality, so equivalent parameterisations are accepted. The 2 px P95 tolerance leaves a large margin over the 0.2 px detection noise; the reference stays below 0.1 px. The 95 % identity and 0.9 clutter thresholds allow a small ambiguous subset but reject gross mismatches. The clock bounds (RMS 0.06 s, max 0.18 s) are also constrained by the dynamic reprojection check, so a clock cannot pass by luck.

Only `/app/calibrate.py` is copied into a separate verifier image. It runs as an unprivileged user; hidden cases and logs are readable by root only. `tests/check.py` writes `ctrf.json` and a per-check `scorecard.json`.

## Data

Joint states are real G1 recordings from OpenHLM (sources and hashes in `DATA_PROVENANCE.json`). Everything optical is synthetic: mounts, camera, clocks, clutter and slips. `generator/` rebuilds every case from the recordings; see `generator/README.md`.
