# G1 slip calibration

Hardware / Robotics. Deliverable: a standalone Python calibration CLI. The forward model is defined by the supplied modules, not by manufacturer geometry. Expert implementation effort has not been measured. A source-based planning estimate is 10–20 focused hours for an expert who already knows the approach; this does not establish the rubric’s few-hours condition. See [reference audit and assumptions](docs/reference-audit.md). Author: lishigong. Email: gonglishi1997@gmail.com. GitHub: gonglishi1997-ai.

## Difficulty explanation

The observations have no persistent marker identities. Clock error changes the joint configuration used to predict an image, while a wrong marker assignment can produce a locally convincing installation transform. Occlusion removes different subsets from different records. A physical mount change must be distinguished from a wrong clock and from coherent false targets following the same arm motion. The solution must reconcile these discrete hypotheses with continuous geometry across complementary records. Both a human specialist and an automated solver must find reliable initialization and reject plausible local minima; simply increasing optimizer iterations is insufficient.

A robotics calibration engineer would perform this work when diagnosing an optical target that moved during a multi-session robot calibration. Real G1 joint-state recordings drive this synthetic benchmark. Optical observations, measurement geometry, clocks, clutter, and mount changes are synthetic. The benchmark has not been validated with physical G1 cameras and does not claim manufacturer-accurate geometry. The state trajectories originate from OpenHLM recordings. Numerical source provenance is included in DATA_PROVENANCE.json. The offline forward-generation audit and truth derivation are documented in tools/truth-audit/README.md.

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

I led the task's scope, acceptance criteria, and evaluation strategy. I required robot-state trajectories to be essential to the solution and chose to test calibration across multiple records and combinations of sensor faults. These decisions shaped the task around joint estimation and generalisation, with difficulty coming from the inference problem rather than additional encoding conventions.

I directed the iteration process through concrete evaluation requirements: independent model runs, explicit separation of infrastructure errors from solution failures, reference-solution validation, and adversarial testing. I used the observed outcomes to choose which designs to retain or revise. After receiving feedback about specification ambiguity, I initiated an audit of all six unsuccessful submissions and requested that a verifier gap be repaired and checked through offline regression tests.

I configured API access, ran and monitored local evaluations, collected execution evidence, and coordinated model substitutions and scope expectations with the recruiter. I also determined what the final submission needed to demonstrate: a reproducible task, a working reference solution, traceable model results, and documented limitations.

## Use of AI tools

I used AI coding tools extensively as development collaborators for implementation, numerical solver development, verifier construction, debugging, and documentation. My role was to direct the problem design and evaluation process, set acceptance requirements, and make iteration and submission decisions. The implementation was AI-assisted rather than independently hand-written; reported outcomes are grounded in execution logs and verifier results, not model self-assessments.

The `expert_time_estimate_hours` value of 20 is the upper end of the disclosed 10–20 hour planning estimate. The recruiter accepted this scope; it has not been measured in a timed human study.

## Submission status (2026-09-29)

See the repository-level reports/RESULTS.md for version-specific results. The latest workload-exception quality review predates the subsequent verifier-only unchanged-arm invariant repair. That repair passed offline reference 8/8 and nine mutation checks; six historical submissions remain overall failures on replay. No six new blind model trials were run for the final submission. Earlier references to unchanged verifier code describe the preceding submission stage.
