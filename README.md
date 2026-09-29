# G1 campaign calibration benchmark

A reproducible robotics-estimation task developed by **lishigong** ([gonglishi1997-ai](https://github.com/gonglishi1997-ai)). Contact: gonglishi1997@gmail.com.

## Start here

- [Task and author/AI contribution disclosure](tasks/g1-slip-calibration/README.md)
- [Results, versions and limitations](reports/RESULTS.md)
- [Chinese fairness audit](evidence/fairness-REPORT_中文.md)
- [Exact changes since evaluated version](evidence/FINAL_VS_EVALUATED.json)
- [Verifier repair](evidence/verifier-fix.patch)
- [Latest quality verdicts](evidence/quality-verdicts.json)

The task is in `tasks/g1-slip-calibration`.

## Evaluation summary

- **Six independent standard trials completed normally and failed the verifier:** GPT-6 Sol / xhigh ×3 and DeepSeek ×3.
- **Reference solution: 8/8 checks passed.**
- **Quality review: 33 pass, 0 fail, and 2 not applicable**, with the recruiter-approved workload exception.
- The verifier repair passed offline regression checks; all six saved submissions remained unsuccessful on replay.

See [the detailed report](reports/RESULTS.md) for evaluation configurations, review scope, and subsequent changes.

Raw traces are available in the [submission release](https://github.com/gonglishi1997-ai/g1-slip-calibration/releases/tag/submission-20260929) as separate evidence ZIPs; see [evidence archive index](reports/ARCHIVES.json). Large logs are excluded from Git history. No online publication of the artifacts is implied by a filename or local path in a historical report.

## Reproduction

Use Harbor `0.23.1.dev202609170426` and Docker. From this repository root:

```sh
harbor run -p tasks/g1-slip-calibration --agent oracle --env docker --yes
harbor run -p tasks/g1-slip-calibration --agent nop --env docker --yes
```

Model runs require separate account access and may incur costs. Review `task.toml` for limits before launching. Model trial environments are fresh; solution and private verifier data must never be copied into the agent image.

The original code/data license and provenance information available with the task is retained. No additional license grant over third-party data is asserted here.
