# Evidence guide

Start with the [evaluation report](../reports/RESULTS.md). This directory preserves evidence from different stages; similar-looking manifests are not interchangeable.

## Which record to use

| Question | Evidence |
| --- | --- |
| What is included in the current task? | [Final task SHA256 manifest](FINAL_TASK_SHA256.json) |
| What exactly did the quality reviewer inspect? | [Reviewed task SHA256 manifest](QUALITY_REVIEWED_TASK_SHA256.json) |
| What changed after the historical model trials? | [Evaluated-to-submission differences](FINAL_VS_EVALUATED.json) |
| What did the quality review conclude? | [Verdicts](quality-verdicts.json), [audit summary](quality-AUDIT_SUMMARY.json), [review provenance](quality-PROVENANCE.json) |
| Which historical runs were valid failures? | [Raw trial audit](RAW_AUDIT.json) |
| What explains the failures and verifier repair? | [Chinese fairness report](fairness-REPORT_中文.md), [first verifier patch](verifier-fix.patch) |
| What was checked after each repair? | [Initial repaired reference](patched-reference/ctrf.json), [time-domain experiments](time-domain/README.md), [delivery follow-up](delivery-fixes/README.md) |

## Archive index layers

- [Archive catalog](../reports/ARCHIVES.json): download URLs, ZIP sizes, and whole-archive SHA256 values.
- [Historical-log member index](EVIDENCE_INDEX.json): paths and hashes of files inside the historical-log ZIP.
- [Audit-archive member index](LATEST_ARCHIVE_INDEX.json): paths and hashes inside the original audit evidence ZIP. Its historical filename does not imply coverage of every later repair; later repair records live in the task/report ZIP and the folders linked above.
- [Redaction note](REDACTION_NOTE.md): explains the first trial's exported numeric-redaction issue and derived readable copies.

`FINAL_TASK_SHA256.json` and `QUALITY_REVIEWED_TASK_SHA256.json` identify different snapshots. Neither replaces the ZIP indexes. Original logs, earlier verdicts, and repair baselines are retained to preserve the audit trail; a later successful check does not erase an earlier result.

## Reading order

1. Read the results summary and scope.
2. Open only the relevant review or repair evidence above.
3. Download the large log archives when detailed trace inspection is needed.

Repair scripts and baseline files are author-side audit material. They are excluded from the task's agent image by its Docker COPY rules. Publicly released cases are suitable for inspection and reproduction, not future unexposed blind evaluations.
