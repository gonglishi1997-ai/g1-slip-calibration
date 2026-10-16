# Data generator

Author-side code; it is not copied into the agent or verifier images.

```sh
python generator/build.py OUT_DIR   # write all public and hidden campaigns to OUT_DIR
python generator/verify.py          # rebuild in a temp dir and compare with the committed cases
```

| File | Role |
| --- | --- |
| `sources/episode_*.json` | four windows of real G1 joint states (OpenHLM), hashes in `../DATA_PROVENANCE.json` |
| `base_campaigns.py` | stage 1: shared rig, per-record clocks, occlusion, frame loss, outliers, ground truth |
| `faults.py` | stage 2: mount slips, ghost target, pixel noise, retransmissions, held-out probes |
| `build.py` | the seed table and the two stages in order |
| `verify.py` | reproducibility check |
| `fixture-sha256.json` | hashes of the committed case files |

Everything is forward-generated from known parameters: the ground truth is what was used to draw the data, never something inferred by a solver.

## Seeds

| Campaign | Base (stage 1) | Final (stage 2) | Notes |
| --- | --- | --- | --- |
| example_a, example_b | 106111, 106102 | 61101, 61102 | public, episode 0 |
| held_a | 681401 | 61901 | hidden, episodes 1, 2, 3 |
| held_b | 681402 | 61902 | hidden, episodes 3, 1, 2 |
| held_no_slip | 681402 | 61903 | same rig as held_b, no slip |

These seeds are public, so the hidden cases are no longer blind. For a new blind evaluation, generate cases with new seeds and keep them out of the repository.

## Reproducibility

With Python 3.12, NumPy 2.3.5 and SciPy 1.17.0, 54 of the 64 files are byte-identical and the other 10 (JSON) match to 1e-10. The small differences are last-digit float rounding.
