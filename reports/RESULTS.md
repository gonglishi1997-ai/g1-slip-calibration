# Results and change history

Short version: the reference solution passes 8/8 checks, and none of the 8 model runs passed. Details below. The evidence for each point is in [`evidence/`](../evidence/README.md).

## Model runs

These runs used an earlier version of the task. The documentation the agent sees changed afterwards (see [Changes after the runs](#changes-after-the-runs)). Each run finished normally and got reward 0. The table shows the first error the verifier reported, not every problem in the program.

| Run | First reported failure |
| --- | --- |
| GPT-6 Sol (xhigh) 1 | Projection errors of 165.2 and 146.5 px |
| GPT-6 Sol (xhigh) 2 | Projection errors of 119.3, 116.4 and 135.0 px |
| GPT-6 Sol (xhigh) 3 | Wrong number of slip segments; projection error of 118.0 px |
| DeepSeek 1 | Negative camera depth |
| DeepSeek 2 | Projection errors of 238.9, 383.1 and 401.2 px |
| DeepSeek 3 | Mount translation above its 0.25 m bound; projection error of 188.6 px |

GPT-6 Sol and DeepSeek also ran one adversarial trial each. Both got reward 0.

I did not count runs that ended in environment errors, API failures, timeouts or safety refusals. Those runs are listed in [`RAW_AUDIT.json`](../evidence/RAW_AUDIT.json). The DeepSeek runs used the Claude Code agent framework, so their log file names mention Claude.

## Was the task fair?

The agent was told the exact conventions: transform direction, how the encoder offset is added, the clock and rolling-shutter formulas, and the slip frame index.

To rule out a convention mix-up, I applied six common fixes to the failed outputs:

- negating the encoder offsets;
- swapping the encoder offsets between arms;
- inverting the camera transform;
- transposing the camera rotation;
- inverting the mount transform;
- transposing the mount rotation.

None of them turned a failure into a pass. That argues against a single shared convention error, but it does not rule out every possible ambiguity.

Full analysis, in Chinese: [`fairness-REPORT_中文.md`](../evidence/fairness-REPORT_中文.md).

## Verifier fix: the unaffected arm

During the audit I found that moving the mount of the arm that did **not** slip by 1 mm still passed, because the change stayed within the pixel tolerance. I added a direct check: across slip segments, the unaffected arm's mount matrices must agree to within 1e-5. The arm that slipped is still scored by projection only.

Tests of the new check:

| Input | Expected | Result |
| --- | --- | --- |
| True answer | pass | pass |
| 1e-7 rounding noise | pass | pass |
| Unaffected arm shifted by 1 mm | fail | fail |
| Unaffected arm rotated by 1 mrad | fail | fail |
| Reference solution | 8/8 | 8/8 |

The six saved model programs were rerun on the three hidden campaigns, 18 runs in total. All six still fail overall. This was re-scoring of saved programs, not new model runs. Code change: [`verifier-fix.patch`](../evidence/verifier-fix.patch).

This bug was too lenient. It could have let a wrong answer pass. It did not cause any of the model failures.

## Other checks added later

- **Time domain.** Every packet's exposure time must fall inside its state recording. Rescoring the saved outputs gave the same results as before: two individual campaigns pass, and all six submissions still fail overall. See [`time-domain/`](../evidence/time-domain/README.md).
- **Stale output.** On bad input, the program must delete any old output file before it exits. All five malformed-input cases are now tested both with and without a pre-existing output file. See [`delivery-fixes/`](../evidence/delivery-fixes/README.md).

After each change, the reference solution passed 8/8 again.

## Changes after the runs

After the model runs I made several changes:

- spelled out the nested keys of the output format;
- merged the documentation;
- added the truth-generation audit scripts;
- fixed a legacy grading entry point;
- added a note on how AI tools were used.

So the agent-facing documents differ from what the models saw. The models were not rerun on the final version. File-level differences are in [`FINAL_VS_EVALUATED.json`](../evidence/FINAL_VS_EVALUATED.json).

An adapted 35-item quality review returned 33 pass, 0 fail and 2 not applicable. It was done before the verifier fixes above.

## Limits

- **Small sample.** Eight model runs on two model families are not enough for a general claim about model ability.
- **Possible gaps.** The table lists first failures, not root causes. No independently written solver has passed the task yet, so a threshold or specification issue I haven't found is still possible.
- **Not blind tests anymore.** The hidden cases, their answers and the reference solution are public. Any new blind evaluation needs freshly generated private cases.
- **Simplified geometry.** The kinematics are a simplified 7-joint arm driven by real G1 joint recordings. The camera detections come from the formula, not from rendering.

Large raw logs are in the GitHub release. Download links and checksums are in [`ARCHIVES.json`](ARCHIVES.json).
