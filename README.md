# G1 slip calibration benchmark

Given unlabeled optical detections across multiple robot-motion records, recover a shared dual-arm calibration, align local clocks, identify markers, reject clutter, and detect target-mount slips.

Real G1 joint-state recordings drive this synthetic benchmark. Optical observations, measurement geometry, clocks, clutter, and mount changes are synthetic. The benchmark has not been validated with physical G1 cameras and does not claim manufacturer-accurate geometry.

Developed by **lishigong** ([gonglishi1997-ai](https://github.com/gonglishi1997-ai)). Contact: gonglishi1997@gmail.com.

## Start here

- [Task design, implementation, and author contributions](tasks/g1-slip-calibration/README.md)
- [Evaluation results and limitations](reports/RESULTS.md)
- [Latest release and downloads](https://github.com/gonglishi1997-ai/g1-slip-calibration/releases/tag/submission-20260929-v3)

The runnable Harbor task is in `tasks/g1-slip-calibration`.

## Results at a glance

The current reference passed **8/8 checks**. Six historical model submissions remained overall failures in offline replay; the six independent model trials were not rerun on the final task.

| Evidence | Result |
| --- | --- |
| Historical independent standard trials | GPT-6 Sol/xhigh ×3 and DeepSeek ×3: all completed normally with reward 0. |
| Offline validation | Reference 8/8; saved submissions remain unsuccessful; repair-specific controls are documented in the results report. |
| Adapted quality review | 33 pass, 0 fail, 2 not applicable, with the recruiter-approved workload exception. |

The quality review preceded subsequent verifier repairs, and model-visible documentation changed after the historical trials. These results do not establish a general model failure rate. [Review scope and changes](reports/RESULTS.md) explain each result.

## Evidence and audits

The [evidence guide](evidence/README.md) explains the review, repair experiments, version manifests, and raw-log indexes. For a short discussion of failure causes, read the [English fairness summary](reports/RESULTS.md#fairness-audit-summary). Large raw logs are distributed separately through the release; [archive names and checksums](reports/ARCHIVES.json) identify them.

## Reproduce the packaged controls

Use Harbor `0.23.1.dev202609170426` and Docker. From the repository root:

```sh
harbor run -p tasks/g1-slip-calibration --agent oracle --env docker --yes
harbor run -p tasks/g1-slip-calibration --agent nop --env docker --yes
```

Model runs require separate account access and may incur costs. Review [`task.toml`](tasks/g1-slip-calibration/task.toml) for resource and time limits. The agent and verifier use separate images; the reference solution and private scoring files are not copied into the agent image.

## Public audit material and future evaluations

This public repository includes the reference solution, held-out case answers and private scoring data, and source generators so the submitted task can be inspected and reproduced. **Those published cases must not be treated as blind tests in future model evaluations.** A new blind evaluation needs independently generated, privately held cases. Removing these files from the current branch would not remove their earlier public Git history or release copies.

Source provenance is recorded in [`DATA_PROVENANCE.json`](tasks/g1-slip-calibration/DATA_PROVENANCE.json). Original source notices available with the task are retained; no additional license grant over third-party data is asserted here.
