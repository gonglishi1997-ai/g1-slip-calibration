# Verifier audit

What I checked about the grader itself, what I found, and what is still open.

## Fixed

**Unaffected arm could drift.** Moving the mount of the arm that did not slip by 1 mm still passed, because the change stayed inside the 2 px tolerance. The verifier now requires that arm's mount to stay the same across regimes (to 1e-5). The arm that slipped is still scored by projection only. Patch: [evidence/verifier-fix-unaffected-arm.patch](../evidence/verifier-fix-unaffected-arm.patch). This made the verifier stricter; it did not cause any model failure.

**Time domain.** The format requires every detection's exposure time to lie inside its state recording. The verifier now checks this for every packet, clutter included. All earlier results were unchanged.

**Stale output.** On corrupted input the program must exit with an error and leave no output file. Each of the five corrupted-input cases is now run twice: once with no output file and once with a stale one already present. The reference solver originally left the stale file in place; it now deletes it first.

## Automated controls

`devtests/test_verifier_controls.py` grades modified versions of the ground truth for each hidden campaign:

| Input | Must | Check that must catch it |
| --- | --- | --- |
| ground truth | pass | – |
| 1e-7 rounding noise on the camera pose | pass | – |
| unaffected arm moved 1 mm / rotated 1 mrad | fail | `unaffected_arm` |
| slip not reported | fail | `slip_count` |
| slip boundary off by 4 frames | fail | `slip_boundary` |
| slip boundary as a float | fail | `segments_valid` |
| all clocks shifted by 0.1 s | fail | `clock_error` |
| every packet rejected as clutter | fail | `association` |
| no packet rejected | fail | `clutter` |
| left and right identities swapped | fail | `association` |
| camera moved 5 cm | fail | `static_projection` |
| encoder offsets negated | fail | `static_projection` |
| focal length out of bounds; mount translation 0.3 m | fail | `output_schema` |
| record missing | fail | `output_schema` |
| extra key | fail | `record_schema` |
| one identity used twice in one image | fail | `associations_valid` |

## Refactoring checks (October 2026)

The verifier was rewritten from one dense file into `check.py` (runner), `grading.py` (one function per check) and `sandbox.py`. To make sure the rewrite changes nothing:

- **Same verdicts.** The old and new graders were run on 61 controlled outputs (the table above plus borderline cases such as a boundary off by exactly 3 frames, fx + 2, a 0.03 s clock shift and the maximum readout time). They agreed on all 61.
- **Same reference result.** The reference solver passes all 8 hidden tests under both the old and the new verifier.
- **Same solver.** The reference solver was reformatted, documented and had two functions renamed. Its syntax tree is otherwise identical to the original.
- **Same data.** The generator was rewritten as plain modules. Regenerating all 64 case files reproduces them exactly: 54 byte for byte and 10 JSON files equal up to 1e-10 float rounding.

## Open issues

These came up during the review and are not fixed:

- **Readout time is weakly tested.** Setting the rolling-shutter readout to its upper bound (0.035 s instead of the true 0.018–0.027 s), with everything else correct, still passes. The arms move slowly enough that the readout error stays under 2 px. A readout check, or faster motion, would close this.
- **The ghost target always uses the same mount offset,** (26, −19, 11) mm, in every campaign. A solver could hard-code it. New cases should randomise it.
- **The reference solver depends on wall-clock time.** It runs two seeds with 60 s and 160 s limits and a fallback with a 100 s limit. On a much slower machine a seed can time out and the answer can change. The solver passes with about 100 s per campaign on 2 CPUs.
- **No independent solver.** Only the reference has passed, so the thresholds have not been calibrated against a second, independently written solution.
