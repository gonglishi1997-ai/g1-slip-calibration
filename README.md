# G1 slip calibration benchmark

A synthetic dual-arm visual calibration task driven by real G1 joint-state recordings. Given multiple records of unlabeled optical detections, a solver estimates shared rig parameters and record-specific clocks, associates detections with markers, rejects clutter, and detects target-mount slips. The supplied modules define the forward model; this project does not claim physical G1 camera validation or manufacturer-accurate geometry.

Developed by **lishigong** ([gonglishi1997-ai](https://github.com/gonglishi1997-ai)). Contact: gonglishi1997@gmail.com.

## Start here

- [Task specification, implementation notes, and author/AI contribution disclosure](tasks/g1-slip-calibration/README.md)
- [Evaluation results, version history, and limitations](reports/RESULTS.md)
- [Chinese failure and fairness audit](evidence/fairness-REPORT_中文.md)
- [Exact task-file changes since the evaluated version](evidence/FINAL_VS_EVALUATED.json)
- [Final verifier repair](evidence/verifier-fix.patch)
- [Quality-review verdicts](evidence/quality-verdicts.json)

The runnable Harbor task is in `tasks/g1-slip-calibration`.

## What the results establish

| Evidence | Result and version |
| --- | --- |
| Historical model evaluation | Three GPT-6 Sol/xhigh and three DeepSeek standard trials completed normally with reward 0 on an earlier frozen task. Those six trials were **not rerun on the final task**. |
| Final verifier checks | The reference passed 8/8 checks after the verifier repair. Nine positive/negative mutation checks passed; the six saved submissions remained overall failures when replayed offline. Replay is not new model inference. |
| Quality review | 33 pass, 0 fail, 2 not applicable under a recruiter-approved exception to the few-hours workload criterion. The review preceded the final verifier-only repair and is not an unmodified upstream approval. |

The final task also has model-visible documentation changes relative to the historical trials. See the [detailed change record](reports/RESULTS.md) for the scope of each result. These observations do not establish a general model failure rate or prove that the task has no ambiguity.

Raw traces are in the [submission release](https://github.com/gonglishi1997-ai/g1-slip-calibration/releases/tag/submission-20260929-v2); [archive names and checksums](reports/ARCHIVES.json) are listed separately. Large logs are excluded from Git history.

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
