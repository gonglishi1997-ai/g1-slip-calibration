# Evaluation summary

This document is bundled with the task so that review does not require access to an external report.

On the frozen evaluation version, GPT-6 Sol/xhigh completed three independent standard runs normally with reward 0, and one valid official-prompt adversarial run normally with reward 0. DeepSeek flash/max likewise completed three valid standard runs and one adversarial run with reward 0. Original environment errors, API failures, safety refusal and timeouts are retained in the external evidence archive and excluded from these counts. These are historical observations, not guarantees for another run.

Reference/oracle and nop controls gave 1 and 0 respectively. The repaired supporting entry point passed all eight reference checks. All 25 static checks passed. Offline forward regeneration reproduced 64 public/private fixture files byte for byte.

The latest quality review (`gpt6-sol-original-waiver-rubric-1`) returned **33 pass, 0 fail, and 2 not applicable**. It applied the 35 upstream criteria at commit `4def1f367467b34b18e0dbdc086400ba71c3e037`, with the recruiter-approved exception for the disclosed, unmeasured 10–20 expert-hour scope. The recruiter also approved GPT-6 in place of Claude. This is an adapted review, not an unmodified upstream approval or a measured human completion time. Earlier review failures remain in the evidence archives.

That review preceded the final verifier repair enforcing the unchanged arm's mount across adjacent regimes. After the repair, the reference passed 8/8 checks and nine positive/negative mutation controls passed. All six saved submissions remained overall failures after offline replay and regrading; this was not six new model runs. Model-visible documentation also changed after the historical trials, so those trials are not retests of the final submission.

Review networking was adapted locally to avoid VPN/egress incompatibility. These results do not claim approval by Terminal-Bench maintainers or equivalence to every hosted deployment.

Full configs and raw logs are provided separately in the submission evidence archives. They are not needed to understand the result summary above and are not copied into the solving environment. See [submission changes](submission-changes.md) and [reference audit](reference-audit.md).
