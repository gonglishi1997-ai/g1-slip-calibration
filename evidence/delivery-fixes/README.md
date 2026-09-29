# Delivery follow-up validation

Baseline: `c58b83a`. No paid model evaluation was run.

## Portable truth regeneration

`comparison-controls.json` records nine comparator controls, including the reported last-digit floating-point difference. Only finite JSON floats may use absolute tolerance 1e-10; integer identities, types, object keys, arrays and labels remain exact. The bundled fixtures are first checked against `tools/truth-audit/fixture-sha256.json`. Generated binary data remain byte-exact. The frozen manifest was captured from the baseline fixtures; no fixture was changed.

`reproduction.json` is a fresh network-disabled Docker regeneration with Python/NumPy/SciPy from the existing verifier image. All 64 files matched byte for byte in this environment. That observation is not a guarantee of byte identity across platforms; use `--strict-bytes` if strict reproduction is required. Run comparator controls with `python evidence/delivery-fixes/check_comparison.py tasks/g1-slip-calibration`.

## Stale output

`stale-probe.json` confirms the original reference left a pre-existing output after malformed input, whereas the new entry point removes it and still exits nonzero. `stale_probe.py` uses `/source` for the task and `/audit` for experiment files; retrieve the baseline reference with `git show c58b83a:tasks/g1-slip-calibration/solution/calibrate.py` as `/audit/reference_before.py` when repeating the comparison. Imports use the verifier image's `/app` modules.

`reference-ctrf.json` and `reference.log` record the complete updated verifier run. Each of its five malformed-input checks now runs with both a fresh output path and a pre-existing output. These remain five CTRF checks, containing ten malformed-input invocations in total. The three calibration campaigns use the unchanged numerical algorithm.

Regression used a network-disabled Docker container, 2 CPUs and 4 GB, with the updated check.py and reference installed into the existing g1-deepseek-verifier:v6 image. This is an offline Docker regression, not a new Harbor model trial. `CHANGE_SCOPE.json` records the reference source change and hashes.

The final release uses a new tag rather than moving the historical tag. Release notes identify the exact commit; the manually uploaded task ZIP is compared against every tracked file before publication.
