# G1 campaign calibration benchmark

A reproducible robotics-estimation task developed by **lishigong** ([gonglishi1997-ai](https://github.com/gonglishi1997-ai)). Contact: gonglishi1997@gmail.com.

## Start here

- [Task and author/AI contribution disclosure](tasks/g1-slip-calibration/README.md)
- [Results, versions and limitations](reports/RESULTS.md)
- [Chinese fairness audit](evidence/fairness-REPORT_中文.md)
- [Exact changes since evaluated version](evidence/FINAL_VS_EVALUATED.json)
- [Verifier repair](evidence/verifier-fix.patch)
- [Latest quality verdicts](evidence/quality-verdicts.json)

The final task is in `tasks/g1-slip-calibration`. Six historical independent standard trials failed normally (GPT-6 Sol/xhigh ×3 and DeepSeek ×3). Those trials used the earlier frozen version; they are **not six new trials of this submission**. Following a verifier repair, all six saved programs were replayed and remained unsuccessful. The reference passed 8/8.

The latest pre-repair quality review returned 33 pass, 0 fail and 2 not applicable, applying the recruiter's accepted 10–20 expert-hour scope exception. The final verifier repair was tested offline, not followed by another paid rubric review. The time estimate is not a measured human completion time.

Raw traces are distributed separately as evidence ZIPs; see [evidence archive index](reports/ARCHIVES.json). Large logs are excluded from Git history. No online publication of the artifacts is implied by a filename or local path in a historical report.

## Reproduction

Use Harbor `0.23.1.dev202609170426` and Docker. From this repository root:

```sh
harbor run -p tasks/g1-slip-calibration --agent oracle --env docker --yes
harbor run -p tasks/g1-slip-calibration --agent nop --env docker --yes
```

Model runs require separate account access and may incur costs. Review `task.toml` for limits before launching. Model trial environments are fresh; solution and private verifier data must never be copied into the agent image.

The original code/data license and provenance information available with the task is retained. No additional license grant over third-party data is asserted here.
