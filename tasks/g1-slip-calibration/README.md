# G1 slip calibration

Hardware / Robotics. Deliverable: a standalone Python calibration CLI. The forward model is defined by the supplied modules, not by manufacturer geometry. Expert implementation effort has not been measured. A source-based planning estimate is 10–20 focused hours for an expert who already knows the approach; this does not establish the rubric’s few-hours condition. See [reference audit and assumptions](docs/reference-audit.md). Author: lishigong. Email: gonglishi1997@gmail.com. GitHub: gonglishi1997-ai.

## Difficulty explanation

The observations have no persistent marker identities. Clock error changes the joint configuration used to predict an image, while a wrong marker assignment can produce a locally convincing installation transform. Occlusion removes different subsets from different records. A physical mount change must be distinguished from a wrong clock and from coherent false targets following the same arm motion. The solution must reconcile these discrete hypotheses with continuous geometry across complementary records. Both a human specialist and an automated solver must find reliable initialization and reject plausible local minima; simply increasing optimizer iterations is insufficient.

A robotics calibration engineer would perform this work when diagnosing an optical target that moved during a multi-session robot calibration. The state trajectories originate from OpenHLM recordings; optical measurements, geometry, clocks, clutter and mount changes are synthetic. This is a controlled analogue of that calibration problem rather than a claim of real sensor validation or exact G1 geometry. Numerical source provenance is included in DATA_PROVENANCE.json. The offline forward-generation audit and truth derivation are documented in tools/truth-audit/README.md.

## Solution explanation

The reference combines full-record and guaranteed-stable-prefix initializations. It fits the shared camera and mounts while recovering each record's independent clock, detects candidate changes, then alternates one-to-one identity assignment and robust continuous optimization. It compares a constant-mount model against a piecewise model after full refinement. A slower pooled full-record initialization is tried only when the completed fits explain fewer than 70% of observations within one pixel. This is an optimization heuristic, not an acceptance criterion. Shared estimates allow a record missing one arm to borrow information from the other records.

The implementation reuses earlier generic calibration routines developed with coding-model assistance. The legacy bootstrap is included as readable nested Python definitions in the one submitted file. It does not access generator seeds, hidden labels or private answer files. The reference output is computed from each invocation's input.

## Verification explanation

Three fixed held-out campaigns exercise different motion and initial calibration, including a no-slip control. The no-slip control shares one initial rig with a slip case and is not a third independent rig source. Each campaign contains three records. Tests evaluate each regime and arm on perturbed held-out joint configurations, recover clock accuracy and packet identity, and check dynamic reprojection. They also reject five malformed binary cases placed in the last record. Input validation must precede output publication.

Transform equality is deliberately not the score: geometrically equivalent parameterizations are accepted. The 2-pixel P95 projection tolerance allows substantial margin over the at-most 0.30-pixel per-axis observation noise, floating-point error and alternative numerical estimators. Reference residuals on these data are below 0.1 pixel. Identity accuracy of 95% and clutter precision/recall of 90% allow a small ambiguous subset while rejecting gross mismatches. Clock RMS 0.060 seconds / maximum 0.180 seconds accommodates numerical timing estimation but is jointly constrained by dynamic reprojection, so a clock cannot earn credit merely by landing inside a broad interval. A three-frame boundary tolerance accommodates sparse sampling around a change. Transform and parameter bounds reproduce the physical input contract, with small numerical slack.

These tolerances have been checked against generator truth and a generic reference, plus negative controls: constant mounts across a real slip, displaced boundaries, all-clutter output, a missing record, and a state-convention change with unchanged camera bytes. They have not yet been validated with an independently developed successful alternative solver. This limitation is explicit; no claim of exhaustive identifiability or adversarial validation is made.

Only /app/calibrate.py transfers into a separate pristine verifier image. Agent code runs in a subprocess as UID/GID 65534; private tests and reward logs are root-only. Root captures output, applies the checks, emits per-test CTRF and decides the binary reward. No network installation occurs during verification. The frozen evaluation version completed one valid zero-reward adversarial trial with each of GPT-6 Sol and DeepSeek; see the bundled [evaluation summary](docs/evaluation-summary.md).

Agent budget: 28800 seconds, the upstream maximum, chosen to honor the request to avoid the previous 90-minute cutoff during formal trials. Timeouts are infrastructure/execution outcomes and never counted as successful model failures. Runtime per submitted campaign is 240 seconds on two CPUs/4 GB; the verifier ceiling is 1000 seconds. These distinguish development effort from the efficiency of the resulting program. The frozen evaluation version passed reference validation; submission changes and their checks are described in the bundled [change summary](docs/submission-changes.md).

## Relevant experience

My academic background is in Information and Computational Science and Mathematics and Statistics. My project experience includes nonlinear least-squares fitting, ordinary differential equation modelling, and mixed-integer optimisation using Python and Gurobi. During a backend development internship, I also contributed to coding, debugging, testing, Git collaboration, and Docker deployment. These experiences provide a foundation for the parameter estimation, constraint modelling, numerical computation, and reproducible evaluation involved in this task. Robot calibration is an application area I explored further through this assignment; I do not claim prior hands-on G1 robot calibration experience.

## Personal contribution

I defined the task goals, requested design revisions, and coordinated local evaluation. During development, I explicitly required state data to participate meaningfully in solving the task and requested evaluation across different records and combinations of faults. These requirements were intended to test generalisation and increase difficulty beyond adding enumerable encoding transformations.

For evaluation, I configured API access, launched tests locally, monitored execution, and collected logs to support investigation of network interruptions, timeouts, and unsuccessful solutions. I also contacted the recruiter to confirm the permitted model substitutions for testing and quality review. The evaluation records retain invalid attempts and distinguish them from model failures after normal completion.

## AI assistance and contribution boundaries

This task was developed with substantial assistance from AI coding tools. The assistants contributed to design refinement, implementation, reference-solution and verifier development, failure analysis, and report preparation. My principal contributions were defining requirements and acceptance constraints, choosing iteration directions, executing local evaluations, and coordinating the submission.

I disclose this assistance explicitly and do not present AI-generated implementation as code I wrote independently. I also do not treat a model's claim of success as equivalent to passing the actual verifier. The submission reports results using reproducible run configurations, original logs, and verifier outputs.

The scalar `expert_time_estimate_hours` in `task.toml` is 20, the conservative upper end of the unmeasured 10–20 hour planning range. It is not a measured completion time or a claim that the few-hours rubric is satisfied.

## Submission status (2026-09-29)

See the repository-level reports/RESULTS.md for version-specific results. The latest workload-exception quality review predates the subsequent verifier-only unchanged-arm invariant repair. That repair passed offline reference8/8 and nine mutation checks; six historical submissions remain overall failures on replay. No six new blind model trials were run for the final submission. Earlier references to unchanged verifier code describe the preceding submission stage.
