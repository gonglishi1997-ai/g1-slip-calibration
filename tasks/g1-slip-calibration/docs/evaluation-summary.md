# Evaluation summary

This document is bundled with the task so that review does not require access to an external report.

On the frozen evaluation version, GPT-6 Sol/xhigh completed three independent standard runs normally with reward 0, and one valid official-prompt adversarial run normally with reward 0. DeepSeek flash/max likewise completed three valid standard runs and one adversarial run with reward 0. Original environment errors, API failures, safety refusal and timeouts are retained in the external evidence archive and excluded from these counts. These are historical observations, not guarantees for another run.

Reference/oracle and nop controls gave 1 and 0 respectively. The repaired supporting entry point passed all eight reference checks. All 25 static checks passed. Offline forward regeneration reproduced 64 public/private fixture files byte for byte.

The latest model rubric review (gpt6-sol-rubric-5) completed with 30 pass, 3 fail and 2 not applicable. It accepted the nested JSON schema clarification, but rejected the few-hours implementation claim (`solvable`, `expert_time_estimate`) and absent local report references (`task_readme`). This documentation revision addresses the missing local references and withdraws the unsupported four-hour estimate. It does not assert that the two substantive effort criteria now pass; no further paid review has been run.

The recruiter approved GPT-6 substitution for the default Claude reviewer according to the author's communication. Reviews used the rubric from upstream commit 4def1f367467b34b18e0dbdc086400ba71c3e037, with local networking adapted to avoid VPN/egress incompatibility. This is not a claim of approval by Terminal-Bench maintainers.

Full configs and raw logs are provided separately in the submission evidence archives. They are not needed to understand the result summary above and are not copied into the solving environment. See [submission changes](submission-changes.md) and [reference audit](reference-audit.md).
