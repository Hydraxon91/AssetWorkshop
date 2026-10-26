# Final adapter review — 2026-10-26

> Historical operator record. The current approved operator is `deepseek/deepseek-flash`;
> see repository `docs/operators.md`. This review was a static read-only pass, not a
> runtime or modelling benchmark.

User requested DeepSeek V4.1 Flash Abliterated after Free usage was exhausted.
`refuseless/deepseek-v4.1-flash-abliterated` responded successfully. Read-only
review session `ses_e877b788effeFeMWt1PkVFXxwt` returned STOPPED; no edits, processes
or Blender access. Parent supplied the four final source/test files, not history.

**Verdict:** no blocker for bounded parameter-only A/repeat-A/B with a single
recorded adapter revision. This was static review, not another runtime test or
agent-operated modelling benchmark.

## Reconciled findings

1. Snapshot and material-copy comparisons do not independently measure material
   slot link modes/object overrides. The current builder creates DATA-linked slots
   only, and copies retain source object channels. Accept as a fixed-recipe scope
   limit, not authority to accept arbitrary manually overridden source materials.
2. Recipe digests do not bind imported module code. Existing runner hashes its
   entry script, not every imported dependency. Final source hashes are already
   recorded in `adapter-result.md`; record/check those module+CLI+recipe identities
   for each benchmark run, with no code changes mid-trial. No new runner needed.
3. The pure preset test is a narrow structure test, not runner acceptance proof.
   Actual geometry/atlas presets were each accepted and completed by the existing
   runner (eight operations apiece). The independent reopened verifier compares
   **UV→baked** sources/corners only; master→prepared→UV preservation relies on
   stage checks against the construction baseline, not that independent comparison.

No corrective source edits or expanded geometry work were needed for this review.
This supersedes the earlier statement that final fixes lacked a fresh independent
review; it does not change the recorded two-box runtime results or their limits.

Next gate remains benchmark scope/parameters and actual editability checks. Model
availability is demonstrated by this response, not guaranteed for future requests.
