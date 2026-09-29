# Reference implementation audit and effort assessment

## Scope and evidence

This audit describes the preserved pre-cleanup reference (1,770 lines). The subsequent stale-output fix adds output-path cleanup before input loading; the numerical algorithm is unchanged. The companion JSON intentionally retains the historical source hash and measurements. Use the final task manifest for the current source hash.

This is a source inspection, not a timed expert implementation study. The reference was not changed during that original audit. The companion JSON records its SHA256 and AST-derived measurements: 1,770 physical lines, 1,615 nonblank/noncomment lines, and 79 function definitions including nested functions. There are no exact duplicate function bodies under a normalization that ignores the function name and source locations. Similar mathematical operations can still be implemented differently. Name-load counts are not a complete call graph.

## Active structure

- Lines 27–807: packet validation, record loading, tracks, clock/pose initialization, correspondence assignment and continuous refinement.
- Lines 808–950: the full-record bootstrap entry point.
- Lines 951–1085: parameter conversion, frame indexing, mount-change detection and piecewise refinement.
- Lines 1086–1138: orchestration. The program invokes itself with `--seed-full` and `--seed-stable`, compares completed fits and conditionally tries a pooled fallback.
- Lines 1140–1763: the 624-line legacy bootstrap, including a second parser, tracking, geometric initialization, assignment/refinement and pooled-record adaptation.
- Lines 1765–1770: CLI dispatch. `--seed-stable` reaches the legacy bootstrap; it is not unused code merely because it is nested in one function.

## Simplification opportunities without changing the task

1. Unify packet decoding and validation behind one representation. The existing parsers have different return contracts and boot handling; replacing one blindly would risk changing semantics.
2. Consolidate repeated camera/transform/clock computations. First reconcile vector layouts and residual definitions: similar equations do not imply interchangeable implementations.
3. Replace implicit parameter slices with named layout helpers to make review easier. This may improve clarity without reducing line count.
4. Consider removing one initialization family only after measuring its contribution across all public, hidden and additional independently generated cases under the runtime limit. Its use in normal CLI dispatch means deletion is an algorithm change, not dead-code cleanup.

No safe large deletion was established in this audit. Whitespace compression, renaming or hiding routines behind modules would not establish lower expert effort. The file contains genuinely distinct recovery strategies, and a shorter implementation has not yet been shown to retain their robustness.

## Effort assessment

The previous four-hour estimate is withdrawn as unsupported. Passing the verifier establishes an executable solution, not the human time needed to write it. The development reused earlier AI-assisted calibration routines, so the observed development process is not evidence for an expert implementing from scratch in four hours.

For planning only, assuming an expert already knows the intended approach and has Python/SciPy and the supplied forward model available, the following is an unmeasured engineering estimate:

| Workstream | Estimated focused hours |
| --- | --- |
| Input validation, output contract and parameter layout | 1–2 |
| Track/clock/geometric bootstrap and identity initialization | 3–6 |
| Shared robust fitting and mount-slip hypotheses | 3–6 |
| Numerical debugging, runtime tuning and integration checks | 3–6 |
| Total | 10–20 |

These ranges are judgments from the code structure, not measured results or proof of a lower bound. Existing reusable solver components may reduce effort substantially; independent design discovery may increase it. A credible few-hours claim needs a timed implementation with the allowed starting assets recorded, or a demonstrably simpler successful solver. Neither is available here.

## Conclusion

Documentation and maintainability can be improved without changing the task, but this audit does not establish that such refactoring can satisfy the rubric's few-hours expert implementation condition. Do not mark `solvable` or `expert_time_estimate` passed on the basis of this document. If strict few-hours compliance is required, obtain implementation evidence or consider a separately versioned reduction in task scope; do not change the benchmark or reuse historical results silently.

The scalar `expert_time_estimate_hours` in `task.toml` is 20, the conservative upper end of the unmeasured 10–20 hour planning range. It is not a measured completion time or a claim that the few-hours rubric is satisfied.
