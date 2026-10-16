# History

**September 2026: task and model runs.** Built the task and ran GPT-6 Sol and DeepSeek (three standard and one adversarial run each). All got reward 0.

**Late September: fixes after the runs.**

- Verifier: added the unaffected-arm check, the packet time-domain check, and the stale-output test.
- Reference solver: now deletes a stale output before validating its input.
- Documentation the agent sees: spelled out the nested output keys and merged the slip rules into one place.

The models were not rerun on this version; the saved programs were re-scored (see [results.md](results.md)).

**October 2026: cleanup, no change in behaviour.**

- Verifier: rewritten as readable modules (`check.py`, `grading.py`, `sandbox.py`). It reports every check in `scorecard.json`, not only the first error. Its verdicts were confirmed identical on 61 controlled outputs.
- Data generator: rewritten as plain modules with one seed table (`generator/`). It reproduces all 64 committed case files.
- Reference solver: formatted, documented, two internal functions renamed. Its syntax tree is otherwise unchanged.
- Agent image: no longer pre-installs a specific coding agent.
- Repository: replaced about 40 intermediate audit files with this `docs/` folder, a compact `evidence/model_runs.json`, and automated verifier tests in `devtests/`.
- Added `sim/`: a MuJoCo run of the real G1 model with rendered marker detection, to measure how far the formula-based observations are from rendered ones.
- Corrupted-input checks now always use the first campaign in sorted order instead of filesystem order.

The agent-facing files (`instruction.md`, `FORMAT.md`, the forward model, the public examples) and all hidden cases are unchanged, so earlier results still apply. Older audit files remain in the git history and in the release archives.
