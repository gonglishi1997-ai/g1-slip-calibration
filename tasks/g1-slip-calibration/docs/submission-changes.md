# Changes relative to the frozen evaluated task

- Author metadata and README now contain the confirmed identity, relevant experience and AI contribution disclosure.
- DATA_PROVENANCE.json and tools/truth-audit provide offline source snapshots, forward constructors, a derivation guide and byte-comparison reproduction.
- The obsolete standalone main in tests/single_grade.py now delegates to the campaign verifier. Existing imported grading/helper function ASTs, tests/check.py, reference solution and scoring data were unchanged by that fix; the new entry passed 8/8 reference checks.
- instruction.md and environment/FORMAT.md now consolidate mount-slip rules, use the absolute deliverable path and specify exact nested output keys. These are model-visible documentation changes. Historical standard/adversarial outcomes apply to the earlier frozen version, not a rerun of this final wording.
- docs now contains a self-contained evaluation summary and reference audit. The unsupported four-hour estimate is withdrawn; a 10–20 hour unmeasured planning estimate is explicitly distinguished from evidence and from rubric compliance.

No task requirements, scoring tolerances or reference algorithm were changed in the source-audit/documentation revision. Author audit material is excluded by the agent/verifier Docker COPY lists. Machine-readable full version hashes are provided in the enclosing submission's CHANGE_MANIFEST.json; this local document states the relevant changes without requiring that external file.
