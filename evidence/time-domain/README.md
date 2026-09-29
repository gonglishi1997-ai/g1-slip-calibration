# Time-domain validation experiment

The verifier now checks the nominal time and observed-row exposure time of every unique packet against the state record bounds, including packets labeled as clutter. This enforces an existing FORMAT.md requirement; the task inputs, reference algorithm and model-visible specification were not changed.

- `check_before.py`: verifier before this update, preserved for comparison.
- `experiment.py` and `RESULTS.json`: seven isolated boundary controls, three truth campaigns, and six real-campaign clock-offset mutations compared before/after the change. All six real-campaign mutations were already rejected by the previous verifier. This is not evidence of an exploitable full-verifier bypass.
- `rescore.py` and `RESCORE.json`: grading of 18 previously saved outputs, without executing the submitted solvers or calling models. Two individual campaign passes remain; all six submissions still fail overall.
- `reference-ctrf.json` and `reference.log`: complete reference-solver regression under the updated verifier.

Experiments ran in a network-disabled Docker container with 2 CPUs and 4 GB memory, using the existing `g1-deepseek-verifier:v6` image. Its 42 case files and both forward-model modules were byte-compared with the current repository. Experiments mounted current tests at `/tests`, forward models at `/app`, this evidence directory at `/audit`, and (for rescoring) preserved replay outputs at `/replay`. The reference run copied the updated verifier and reference program into the existing image and invoked `python /tests/check.py /app/calibrate.py`.

The isolated controls exercise both state-range endpoints, nominal-time violations whose adjusted exposure remains valid, exposure-only violations, and nonfinite time. They do not prove exhaustive behavior for every possible parameterization. No new model or rubric run was performed.
