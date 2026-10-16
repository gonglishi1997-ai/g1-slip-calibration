# Model results

All runs are from September 2026, on an earlier version of the task (see [history.md](history.md)). Each counted run finished normally and got reward 0. The table shows the first error the verifier reported for each failing campaign; at that time the verifier stopped at the first error, so later problems in the same program are unknown.

## Counted runs

| Run | Prompt | Hidden tests passed | First reported failures |
| --- | --- | --- | --- |
| GPT-6 Sol 1 | standard | 6 / 8 | projection error 165.2 px, 146.5 px |
| GPT-6 Sol 2 | standard | 5 / 8 | projection error 119.3, 116.4, 135.0 px |
| GPT-6 Sol 3 | standard | 6 / 8 | wrong number of slip regimes; projection error 118.0 px |
| GPT-6 Sol adversarial | adversarial | 5 / 8 | program tried to write into the read-only input directory |
| DeepSeek 1 | standard | 5 / 8 | negative camera depth in all three campaigns |
| DeepSeek 2 | standard | 5 / 8 | projection error 238.9, 383.1, 401.2 px |
| DeepSeek 3 | standard | 4 / 8 | mount translation above 0.25 m; projection error 188.6 px; accepted a conflicting duplicate packet |
| DeepSeek adversarial | adversarial | 5 / 8 | projection error 420 429 px and 567 px |

"Hidden tests" are the 3 campaigns plus the 5 corrupted-input cases. Most programs handled the corrupted inputs; the geometry is where they failed. GPT-6 Sol ran in the Codex agent, DeepSeek in the Claude Code agent framework.

## Excluded runs

Five runs ended with an infrastructure or agent error and were replaced: two GPT-6 Sol runs that produced no program, one GPT-6 Sol adversarial run that ended in a safety refusal, one DeepSeek run with an API error and one with an agent timeout. The DeepSeek run that hit the API error is worth noting: its unfinished program was the closest any model came, with projection errors of 10–84 px. Full list: [evidence/model_runs.json](../evidence/model_runs.json).

## Was it a convention mix-up?

The agent is told every convention: transform direction, where the encoder offset is added, the clock and rolling-shutter formulas, and how slip frames are indexed. To rule out a misread convention, I applied six common fixes to every failed output:

- negating the encoder offsets;
- swapping the encoder offsets between arms;
- inverting the camera transform, or transposing its rotation;
- inverting the mount transform, or transposing its rotation.

None turned a failure into a pass. This argues against a single shared convention error, but it does not rule out every possible ambiguity. No independently written solver has passed the task yet, so a threshold or specification problem I have not found is still possible.

## Re-scoring after verifier changes

Later verifier changes (see [audit.md](audit.md)) were checked by re-running the six saved standard-run programs on the three hidden campaigns (18 runs). All six still fail overall. This was re-scoring of saved programs, not new model runs.

## Raw logs

The full agent logs are in the GitHub release; links and checksums are in [evidence/archives.json](../evidence/archives.json).
