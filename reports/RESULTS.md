# Evaluation and change record

## Summary

The current reference passes **8/8 checks**. All six historical model submissions remain overall failures on offline replay. The six independent model trials were not rerun on the final task; the adapted quality review also predates later verifier repairs. The sections below distinguish these results and their scope.

## Fairness audit summary

The observed failures involve geometry, event counts, physical parameter bounds, and malformed-input handling. Six limited output-convention transformations did not rescue a failed campaign, so the available evidence does not support one shared sign convention as the sole explanation. This is not an exhaustive ambiguity audit or proof of each solver's internal failure mechanism.

The audit found an overly permissive unchanged-arm check, which was repaired and validated with positive/negative controls. Later time-domain and stale-output checks improved coverage of the stated contract. Reference regressions passed; historical output regrading is distinct from fresh model inference. See the [full Chinese audit](../evidence/fairness-REPORT_中文.md) and [evidence guide](../evidence/README.md) for the supporting records.

## Historical frozen evaluation

These are standard trials on the earlier frozen task, before the final model-visible documentation changes. Each listed run completed normally and received reward 0. The table reports the verifier's first or principal failure, not every underlying cause.

| Run | Principal reported failure |
| --- | --- |
| GPT-6 Sol/xhigh 1 | Static projection errors of 165.225 and 146.516 px |
| GPT-6 Sol/xhigh 2, repaired environment | Errors of 119.254, 116.421, and 134.980 px |
| GPT-6 Sol/xhigh 3, repaired environment | Wrong mount-regime count; 118.030 px error |
| DeepSeek 1 | Negative camera depth |
| DeepSeek 2, replacement | Errors of 238.871, 383.069, and 401.222 px |
| DeepSeek 3, replacement | Mount translation outside its bound; 188.613 px error; conflicting duplicate handling |

GPT-6 Sol and DeepSeek each also completed one adversarial run with reward 0 on the earlier task. Historical environment errors, API failures, timeouts, and safety refusals are preserved but excluded from valid failure counts; [the raw audit](../evidence/RAW_AUDIT.json) identifies the runs. DeepSeek used the Claude Code agent framework, so its log filename does not identify the model as Claude.

## Submission changes and quality review

The submission later added explicit nested output keys, consolidated documentation, supplied truth-generation audit material, corrected a legacy grading entry point, and added author/AI contribution disclosure. Agent-visible documents therefore differ from the historical trials; the six standard trials were not rerun on the final version. [File hashes](../evidence/FINAL_VS_EVALUATED.json) identify the differences.

The recruiter accepted the disclosed, unmeasured 10–20 expert-hour scope and approved GPT-6 in place of Claude for the quality review. The review applied the 35 upstream criteria at commit `4def1f367467b34b18e0dbdc086400ba71c3e037` with that workload exception and returned **33 pass, 0 fail, and 2 not applicable**. This was a recruiter-adapted review, not an unmodified upstream approval or a timed human implementation study. It preceded the verifier repair below.

## Verifier repair after the review

An audit found that a 1 mm change to an unaffected arm's post-slip mount could pass. A new check compares that arm's matrices in adjacent regimes with a tolerance of `1e-5`; ground truth is used only to identify the arm that did not slip. The affected arm is still scored by geometric projection. This repair did not change task instructions, data, or the reference solution.

After the patch, the reference passed 8/8 checks and nine positive/negative mutation controls passed. The six saved programs were replayed on three campaigns (18 executions); all six remained overall failures. This is offline replay and regrading, **not new blind model inference**. The [patch](../evidence/verifier-fix.patch) and [Chinese supplemental audit](../evidence/fairness-REPORT_中文.md) document the change.

## Interpretation and limits

Six limited output-convention transformations did not rescue any failed campaign. The model-visible materials specified column-vector transforms, additive joint offsets, clock formulas, and local namespaces. This is evidence against one common sign convention explaining all failures; it does not rule out every ambiguity or implementation error. First-failing assertions do not identify all root causes. No independently developed successful alternative solver has yet calibrated the original task's thresholds.

The unaffected-arm omission was a permissive false-acceptance issue, not the reason for the original model failures. Earlier quality-review failures remain historical evidence. Exploratory simplified versions v7–v15 were separate experiments, some passed by GPT, and are not counted as failures on this task. Repeated task development and selection limit generalization of the observed outcomes.

Local model runtime and network adaptations are documented in the archived evidence; they should not be equated with every hosted deployment. One adversarial failure is not proof of exploit resistance. The publicly released reference solution and held-out labels make these particular cases unsuitable as future blind tests; new blind evaluations require fresh privately held cases.

## Explicit time-domain checks

A subsequent offline audit added direct checks that every unique packet's nominal time and row-adjusted exposure time lie within its state record. Observed rows are used, including clutter packets. Seven isolated boundary controls passed. Six clock-offset mutations on the existing campaigns were already rejected before this change; these experiments do not demonstrate a previously successful grading bypass. Rescoring 18 saved outputs preserved the same two individual campaign passes and six overall unsuccessful submissions. See [time-domain experiment results](../evidence/time-domain/RESULTS.json) and [rescoring](../evidence/time-domain/RESCORE.json). No model inference was performed.

The full reference regression after this time-domain update passed **8/8** checks; [CTRF results](../evidence/time-domain/reference-ctrf.json) and [execution log](../evidence/time-domain/reference.log) are retained.

## Delivery follow-up

The reference entry point now removes a pre-existing requested output before validating input, and each of the five malformed-input checks covers both a fresh output path and a stale output. FORMAT.md explicitly states this behavior. These changes postdate the historical trials and do not constitute new model evaluations. Numerical estimation code and all frozen fixtures remain unchanged.

Truth regeneration first verifies the frozen fixtures against their strict hash manifest. Regenerated JSON floats allow absolute roundoff up to 1e-10 (no relative tolerance), with types, structure, integer identities and nonnumeric values checked exactly; binary files remain byte-exact. `--strict-bytes` retains the stronger reproduction mode.

The new `submission-20260929-v2` release is pinned to its final repository commit; its uploaded task archive and GitHub-generated source archives describe the same source version. The earlier release remains as historical delivery evidence.

The follow-up offline Docker regression passed **8/8** checks, including both fresh and stale-output invocations for all five malformed-input categories. [Evidence and comparison controls](../evidence/delivery-fixes/README.md) are included.

The subsequent `submission-20260929-v3` release reorganizes documentation and adds an evidence guide. It preserves all prior evidence paths and makes no changes to the solver, verifier, input fixtures, or agent-facing specification.
