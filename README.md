# G1 slip calibration

A Terminal-Bench task that tests whether an AI coding agent can do multi-step physical inference, not just write code that runs.

The agent gets joint-state recordings from a dual-arm robot and unlabelled bright-spot detections from one camera. It has to write a program that recovers the full calibration of the rig, and notice whether a target on one arm slipped partway through a recording.

## The problem

Each arm carries a target with 6 markers. A marker at point `p` on the target appears at pixel `u`:

```
u = project( Y · FK(q(t) + δ) · X · p )
```

| Symbol | Meaning | Known to the agent |
| --- | --- | --- |
| `p` | marker position on the target | yes |
| `X` | mount of each target on its arm's end flange | no |
| `FK(q + δ)` | forward kinematics of the recorded joints `q` plus encoder zero offsets `δ` | `q` yes, `δ` no |
| `Y` | camera pose relative to the robot base | no |
| `project` | pinhole camera with focal lengths `fx, fy` and radial distortion `k1, k2` | no |
| `t` | exposure time: a quadratic clock per recording plus a rolling-shutter row delay | no |

Five faults are added, each blocking a shortcut:

- **Unlabelled detections and clutter.** Spots have no identities, and about a quarter of them come from a ghost target that moves with the arm.
- **Unsynchronised clocks and rolling shutter.** A wrong time picks the wrong joint angles.
- **Mount slip.** In some recordings one target moves partway through; the agent must find which arm and which frame.
- **Encoder zero offsets,** to be estimated together with the camera pose.
- **Corrupted input files,** which must be rejected without writing any output.

The joint angles are real G1 recordings (OpenHLM). The kinematic chain is a simplified 7-joint arm, and the camera detections are generated from the formula above, not rendered.

## Scoring

Behaviour is scored, not parameters: several parameter sets explain the same pixels, so comparing `X` and `Y` directly would reject correct answers. The verifier runs the submitted program on three hidden campaigns (three recordings each, one campaign without any slip) and checks:

| Check | Threshold |
| --- | --- |
| Projection on held-out joint configurations, per arm and mount regime | P95 ≤ 2 px (noise is 0.2 px) |
| Projection at the true detection times, using the submitted clocks | P95 ≤ 2 px |
| Marker identities | ≥ 95 % correct |
| Clutter rejection | precision and recall ≥ 0.9 |
| Slip | right number of regimes, boundary within 3 frames, other arm unchanged |
| Clock | RMS ≤ 0.06 s, max ≤ 0.18 s |
| Corrupted inputs | all five rejected, no output left behind |

The reward is 1 only if everything passes. The verifier also writes `scorecard.json` with every individual check, so a failure shows what went wrong and not just the first error.

## Results

The reference solution passes, with residuals below 0.1 px. Eight model runs (GPT-6 Sol and DeepSeek, three standard and one adversarial run each) all got reward 0. The failures were not near misses: most were projection errors of 116–401 px against a 2 px threshold; others were negative camera depth, a mount outside its physical bound, and a wrong slip count.

To check that models were not failing on an ambiguous convention, I applied six common convention fixes to their outputs (negating or swapping the encoder offsets, inverting or transposing the camera and mount transforms). None turned a failure into a pass.

Details: [docs/results.md](docs/results.md).

## Auditing the verifier

A grader needs known-good and known-bad cases just like the thing it grades. While auditing I found that moving the mount of the arm that did **not** slip by 1 mm still passed, because the change stayed inside the pixel tolerance. I added a direct check, and the saved model programs still fail after re-scoring.

`devtests/` now holds these controls as automated tests: the ground truth must pass, harmless rounding must pass, and 16 kinds of defect must each fail on the check meant to catch them. Other findings and their status are in [docs/audit.md](docs/audit.md).

## Limitations

- **Small sample.** Eight runs on two model families cannot support a general claim about model ability.
- **Simplified geometry, synthetic optics.** Nothing here has been tested on a physical robot or camera. A MuJoCo check with the real G1 model and rendered camera images ([sim/](sim/)) gave 93 % detection rate and 2.2 px P95 detection error, much worse than the 0.2 px noise assumed here.
- **Not blind any more.** The hidden cases and the reference solution are public. A new evaluation needs freshly generated private cases (`generator/` can do this with new seeds).
- **Runs predate later fixes.** The model runs used an earlier version of the task documentation. After the verifier fixes I re-scored the saved programs but did not rerun the models.

## Repository layout

```
tasks/g1-slip-calibration/
  instruction.md, task.toml   what the agent sees; task settings
  environment/                agent image: FORMAT.md, forward model, two public examples
  solution/calibrate.py       reference solver
  tests/                      verifier: check.py (runner), grading.py (checks), hidden cases
  generator/                  rebuilds every case from the joint-state recordings
devtests/                     tests of the verifier, task files and corrupted-input handling
sim/                          MuJoCo check: real G1 model, rendered camera, blob detection
docs/                         results, audit notes, change history
evidence/                     model-run summary, verifier patch, links to raw logs
```

## Running it

The task runs under Harbor (Terminal-Bench's runner) with Docker:

```sh
harbor run -p tasks/g1-slip-calibration --agent oracle --env docker --yes   # reference: reward 1
harbor run -p tasks/g1-slip-calibration --agent nop --env docker --yes      # empty agent: reward 0
```

Developer checks (Python 3.12, `pip install numpy==2.3.5 scipy==1.17.0 pytest`):

```sh
pytest devtests                                        # verifier controls, about 10 s
python tasks/g1-slip-calibration/generator/verify.py   # regenerate all cases and compare, about 5 min
```

## How I used AI

Most of the code was written with coding agents: the reference solver, the verifier and the data generator. I defined the problem, the observation model, the faults, the checks and their thresholds; I ran the model evaluations, did the failure audit that found the verifier bug, and decided what to fix. The solver in particular is a long file I have documented but not rewritten.

Author: Lishi Gong · gonglishi1997@gmail.com · the files carry the Terminal-Bench canary string `harbor-canary GUID 26b5c67b-…` so that the task can be detected in training data.
