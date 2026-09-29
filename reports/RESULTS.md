# Evaluation and change record

## Historical frozen evaluation

| Run | Outcome | Principal reported failure |
|---|---|---|
| GPT-6 Sol/xhigh 1 | Normal reward 0 | 165.225/146.516px static projection errors |
| GPT-6 Sol/xhigh 2 repaired environment | Normal reward 0 | 119.254/116.421/134.980px errors |
| GPT-6 Sol/xhigh 3 repaired environment | Normal reward 0 | Wrong regime count;118.030px error |
| DeepSeek 1 | Normal reward 0 | Negative camera depth |
| DeepSeek 2 replacement | Normal reward 0 | 238.871/383.069/401.222px errors |
| DeepSeek 3 replacement | Normal reward 0 | Mount translation bound,188.613px error, conflicting duplicate handling |

GPT and DeepSeek each also completed one adversarial run with reward0 on the earlier evaluated version. Historical environment, API, timeout and safety-refusal attempts are preserved and excluded from valid failure counts. See RAW_AUDIT.json for exact runs. DeepSeek used the Claude Code agent framework; its log filename does not mean the Claude model was used.

## Submission changes and quality review

Later submission changes added explicit nested output keys, consolidated documentation, supplied truth-generation audit materials, corrected the legacy grading entry point and added confirmed author/AI disclosure. Agent-visible documents therefore differ from the historical trials. FINAL_VS_EVALUATED.json gives exact file hashes.

The recruiter accepted the disclosed 10–20 expert-hour scope and approved using GPT-6 in place of Claude for the quality review. The effort estimate has not been measured in a timed human study. The latest review applied the 35 upstream criteria at commit `4def1f367467b34b18e0dbdc086400ba71c3e037`, with the accepted workload exception, and returned **33 pass, 0 fail, and 2 not applicable**. This result reflects the agreed exception rather than an unmodified upstream approval.

## Verifier repair after that review

An audit showed a1mm change to an unaffected arm's post-slip mount could pass. A new check compares that arm's adjacent matrices with tolerance1e-5, using truth only to identify which arm did not slip. Geometric acceptance for the affected arm is unchanged. No task instruction, data or solution was changed by this repair.

The patched original task passed reference8/8 and9positive/negative mutation controls. Six saved programs were replayed on three campaigns (18executions); regrading with the repair left all six overall failures. This is offline replay, not new model inference. The final task combines the documented submission copy with this exact check.py patch; the full source difference is retained.

## Interpretation and limits

Six limited output-convention transformations did not rescue any failed campaign. Clear column-vector transforms, additive joint offsets, clock formulas and local namespaces were already specified. This is evidence against one common sign convention explaining all failures, not proof that every potential ambiguity or one-line repair has been ruled out. First-failing assertions do not identify all root causes. No fully independent successful alternative solver has yet calibrated the old task's thresholds.

The unchanged-arm omission was a permissive false-acceptance issue, not a reason the original models failed. All prior quality failures remain historical evidence. Exploratory simplified versions v7–v15 were separate experiments, some passed by GPT; their results are not counted as old-task failures. Repeated task development/selection limits generalization of observed failure rates.

Local model runtime/network adaptations are documented in original evidence. The current task retains its declared network policy; do not equate local adapted runs with every hosted deployment. One adversarial failure is not a proof of exploit resistance.
