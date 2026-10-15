# G1 slip calibration

A Terminal-Bench task I built in September 2026. An AI coding agent gets joint-state recordings from a dual-arm robot and unlabeled bright-spot detections from a camera, and has to write a program that recovers the full calibration. It also has to notice whether a target on one arm slipped partway through a recording.

I built it to answer one question: can current coding agents do multi-step physical inference, not just write code that runs?

## What the agent has to recover

Each arm carries a target with 6 markers. One camera watches both arms. A marker at point `p` on the target shows up at pixel `u`:

```
u = project( Y · FK(q(t) + δ) · X · p )
```

| Symbol | Meaning | Known? |
| --- | --- | --- |
| `p` | marker position on the target | yes |
| `X` | how each target is mounted on the arm's end flange | no |
| `FK(q + δ)` | forward kinematics; `q` is the recorded joint angle, `δ` is an encoder zero offset | `q` yes, `δ` no |
| `Y` | camera pose relative to the robot base | no |
| `project` | pinhole projection with focal lengths `fx, fy` and radial distortion `k1, k2` | no |
| `t` | exposure time of the pixel: a separate quadratic clock per recording, plus a rolling-shutter row delay | no |

On top of that, I added five faults. Each one blocks a shortcut:

- **Unlabeled detections plus clutter.** The agent has to match spots to markers in every frame, including false targets that move with the arm.
- **Unsynchronized clocks plus rolling shutter.** A wrong time picks the wrong joint angles.
- **Mount slip.** In some recordings one target moves partway through. The agent has to say which arm and which frame.
- **Encoder zero offsets.** These have to be estimated together with the camera pose.
- **Corrupted input files.** These must be rejected without leaving any output behind.

## How it is scored

I score behaviour, not parameters. The same observations can be explained by several equivalent parameter sets, so comparing `X` and `Y` directly would reject correct answers. The checks are:

- **Pose prediction:** projection error on held-out joint configurations, P95 ≤ 2 px. Observation noise is at most 0.3 px.
- **Dynamic reprojection:** P95 ≤ 2 px.
- **Marker identity:** at least 95% correct. Clutter rejection precision and recall at least 0.9.
- **Slip:** the right number of segments, and the boundary within ±3 frames.
- **Clock:** RMS error ≤ 0.06 s, max ≤ 0.18 s.
- **Malformed input:** all five corrupted-file cases rejected.

There are three hidden campaigns with three recordings each. One of them is a no-slip control. The agent and the verifier run in separate Docker images. Answers are readable only by the verifier.

## Results

- **Reference solution:** passes 8/8 checks, with residuals below 0.1 px.
- **GPT-6 Sol:** 3 standard runs and 1 adversarial run. All got reward 0.
- **DeepSeek:** 3 standard runs and 1 adversarial run. All got reward 0.

The failures were not near misses. Most were projection errors of 116–401 px against a 2 px threshold. Other failures were negative camera depth, a mount translation outside its physical bound, and a wrong slip count.

Per-run details are in [reports/RESULTS.md](reports/RESULTS.md).

To check that I wasn't failing models because of an ambiguous spec, I applied six common convention fixes to their outputs: flipping or swapping the encoder offset, and inverting or transposing the camera and mount transforms. None turned a failure into a pass.

## A bug I found in my own verifier

While auditing, I found that moving the mount of the arm that did **not** slip by 1 mm still passed. The change was inside the pixel tolerance. I added a check that the unaffected arm's mount stays the same across segments, to within 1e-5.

I then tested the check with known inputs:

- **Should pass, and did:** the true answer; 1e-7 rounding noise.
- **Should fail, and did:** a 1 mm shift; a 1 mrad rotation of the unaffected arm.

The reference still passes 8/8. All six saved model programs still fail. This was offline re-scoring of the saved programs, not new model runs. The patch is in [evidence/verifier-fix.patch](evidence/verifier-fix.patch), and the full audit, in Chinese, is in [evidence/fairness-REPORT_中文.md](evidence/fairness-REPORT_中文.md).

The main lesson for me: a grader has to be tested with known-good and known-bad cases, just like the thing it grades.

## Limitations

- **Simplified geometry.** The joint angles come from real G1 recordings (OpenHLM), but the kinematic chain in `kinematics.py` is a simplified 7-joint arm, not manufacturer geometry. The camera detections are generated from the formula above, not rendered. Nothing here has been tested on a physical robot or camera.
- **Small sample.** Eight model runs on two model families can't support a general claim about model ability.
- **Reruns.** The model runs used an earlier version of the task documentation. After the verifier fixes I re-scored the saved outputs but did not rerun the models.
- **Not blind tests anymore.** The hidden cases and the reference solution are now public.

## Next step

Load the real G1 model in MuJoCo, render the markers with a simulated camera, detect them from images, and run the same pipeline. This would show how much error comes from detection, occlusion and motion blur, which the formula-based data leaves out.

## How I used AI

Most of the code was written with coding agents. That covers the reference solver (`solution/calibrate.py`, a long single file I haven't refactored), the verifier, and the data generators. I defined the problem, the observation model, the faults, the checks and their thresholds. I ran the model evaluations, and I did the failure audit that found the verifier bug.

## Repository layout

```
tasks/g1-slip-calibration/
  instruction.md        what the agent sees
  environment/          FORMAT.md, kinematics.py, camera_model.py, public examples
  solution/             reference solver
  tests/                verifier and hidden cases
reports/RESULTS.md      detailed results and change history
evidence/               audit records, verifier patch, raw-log indexes
```

## Run it

Requires Harbor `0.23.1.dev202609170426` and Docker. From the repository root:

```sh
harbor run -p tasks/g1-slip-calibration --agent oracle --env docker --yes   # reference, should pass
harbor run -p tasks/g1-slip-calibration --agent nop --env docker --yes      # empty agent, should fail
```

Author: Lishi Gong · gonglishi1997@gmail.com
