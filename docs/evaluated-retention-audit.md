# Evaluated-retention audit — demonstrated gap and implementation

Status: **audit complete, helper implemented and tested.** The extension proposed by the
audit was approved and built: `pipeline/retention.py`, `scripts/check_retention.py`,
`fixtures/test_retention.py` and `fixtures/check_retention.py`. It is evidence, not a
blocking stage gate; promoting it to one needs separate approval. No asset geometry was
changed and no project gate was altered. The only behavioural change to existing code is
the empty-source guard in `assembly_preservation`.

## Question

Did an edit remove most of the evaluated body while leaving healthy authored sources, and
would the existing helpers notice?

The distinction matters because the tracked helpers answer three different questions:

- `pipeline/preservation.py` compares **authored** representation (geometry/UV/transform/
  material/image field hashes) and states in its own limits that no evaluated
  equivalence is established.
- `pipeline/check.py:assembly_preservation` compares evaluated **source** points to
  **split output part** points, bidirectionally, at 1e-5 m.
- `pipeline/check.py:mesh_health` reads `obj.data`, the authored mesh, and never
  evaluates a modifier stack.

None of them asks "did the evaluated body shrink relative to before the edit".

## Reproduced case

Recorded in round61 as the truck editability failure
(`docs/3d-workflow-review.md`, row R61): six of eight source moves lose most of the body
while the output is nonempty and the source meshes are healthy. The recorded trigger is
`Cab_Roof.001` translated `+0.02` in Z against the `Connect_RearBulkhead` Boolean on
`Truck_MainShell`.

Reproduced on an owned disposable background process, on a byte copy of the exact pilot
input:

- source `round61/pilot61_input.blend`, `sha256 30ca2cddcfc67e77…`, copied to
  `.dev-shots/retention-pilot-01/work/pilot_input_copy.blend` (identical hash)
- Blender 5.2.3 LTS, `--background --factory-startup --disable-autoexec`
- never saved, never exported, `saved_anything: false`
- probe `.dev-shots/retention-pilot-01/retention_probe.py`, result
  `.dev-shots/retention-pilot-01/run-01/result.json`

| State | Roof Z | Evaluated verts | Evaluated spans | Authored verts/faces | Authored sha (first 14) |
| --- | --- | --- | --- | --- | --- |
| C0 baseline | 0.00 | 3861 | 1.666 × 0.759 × 0.501 | 348 / 356 | `45d031777bd0b3` |
| C1 roof +0.02 Z | 0.02 | **701** | **0.527 × 0.600 × 0.227** | 348 / 356 | `45d031777bd0b3` |
| C2 restored | 0.00 | 3861 | 1.666 × 0.759 × 0.501 | 348 / 356 | `45d031777bd0b3` |

The C1 numbers match the recorded round61 case exactly (`701` vertices, `649` faces, span
X `0.527`), so this is the same failure, not a look-alike. Vertices retained 18.2%, X span
retained 31.6%. C2 reproduces C0 exactly, which also shows the trigger is deterministic
and fully reversible — the probe left no residue in the copy.

## What the existing helpers reported

| Helper | C0 | C1 (81.8% of vertices gone) |
| --- | --- | --- |
| `preservation`-style authored fingerprint | unchanged | **unchanged** |
| `mesh_health(require_closed=False)` | `ok: true` | **`ok: true`, no failures** |
| `assembly_preservation` vs a part built from the evaluated result | `ok: true`, 0 failures | **`ok: true`, 0 failures** |

Three green results, one collapsed model.

## The demonstrated gap

Two independent reasons, both structural rather than a threshold being set wrongly:

1. **`mesh_health` cannot see it.** It inspects `obj.data`. A modifier-generated collapse
   leaves the authored mesh byte-identical, so the health gate is blind to it by
   construction. This is not a tolerance question.
2. **`assembly_preservation` validates the wrong pair.** It asks whether the split part
   matches the source it came from. A collapsed source produces a perfectly faithful
   collapsed part, so the comparison passes. It is a transfer check, and the transfer
   succeeded; the body was lost before the split.

`preservation` is explicitly scoped to authored fields and states the limitation, so it is
not defective — but the operator reading "preservation ok" is likely to read it as "the
model is intact", which is what the round61 record shows happened.

Secondary finding: when an evaluated source has **no** vertices, `assembly_preservation`
raises `ValueError('max() iterable argument is empty')` from the `max()` over an empty
point set instead of returning a failure record. Verified synthetically on two empty-mesh
objects in the same run; the real asset never reached zero vertices, so this is a
robustness observation, not evidence about the truck.

## Implemented extension

Built as proposed, with one change of mind recorded below:

1. **Record evaluated metrics per object** — `pipeline/retention.py:snapshot` records
   evaluated vertex and triangle counts, world bbox, per-axis spans and component count,
   plus authored counts and modifier names for context. Read-only; the caller supplies the
   scene and the helper never opens or saves a file.
2. **Compare against the recorded metrics** — `compare` is pure and reports per-object
   retained ratios for `min_vertex_ratio`, `min_triangle_ratio`, `min_span_ratio` and
   `min_bbox_coverage`. Status is `pass`, `fail` or `error`; an undefined measure or an
   empty baseline is `error`, never a pass.
3. **No default threshold.** Each listed object must state at least one criterion, and
   criteria that are not stated are reported as `unchecked`.
4. **Empty-source guard** in `assembly_preservation`, as proposed.

Change of mind: the first draft had an `allow_missing` exception, mirroring
`preservation`. It was removed before testing because it is self-contradictory — a rule
that requires retention plus a licence for the object to vanish cannot both hold, and the
version that "passed but was flagged" would have been a silent acceptance path. A listed
object now must exist in both snapshots; a deliberate deletion does not belong in the
policy. This is recorded because the removal is a scope reduction, not an oversight.

### Verification

- `fixtures/test_retention.py` — 20 pure tests, pass.
- `fixtures/check_retention.py` — 11 Blender checks, exit 0. It pins the defect directly:
  an intact body passes; a boolean-driven collapse that leaves 5% of one axis fails; the
  authored mesh is unchanged and `mesh_health` still reports `ok` across that collapse; a
  total removal reports zero rather than crashing; the `assembly_preservation` guard
  reports a failure instead of raising; unstated criteria come back `unchecked`; a missing
  object fails; an empty baseline is `error`. Restoring the stack measures intact again.
- A useful measurement fell out of the fixture: the collapsed slab keeps **all 8
  authored vertices and all triangles** — `min_vertex_ratio` and `min_triangle_ratio` are
  both `1.0` — so counts alone would call it retained. Only the extents caught it
  (`min_span_ratio` and `min_bbox_coverage` both `0.05`). That is why the module reports
  four measures and why the limits say extents are not shape.
- Real-asset pilot through the CLI on the disposable copy (`.dev-shots/retention-pilot-01/run-02`):

| Measure | New helper | Round61 ad-hoc probe |
| --- | --- | --- |
| `min_vertex_ratio` | 0.181559 | 0.18156 |
| `min_span_ratio` | 0.31637 | 0.31637 |
| `min_bbox_coverage` | 0.103337 | 0.10334 |
| `min_triangle_ratio` | 0.176806 | — |

  The two implementations agree to five decimals while sharing no code, which is the
  useful part: the helper measures the same thing the hand-written case did.
  Controls: identical before/after → `pass`, exit 0; policy with an empty rule → exit 2
  and no report written; writing over an existing report → exit 2. The copy's bytes were
  unchanged after the run.
- Existing regressions re-run and unchanged: `test_preservation.py` 12,
  `test_pipeline.py` 12, `test_exposure.py` 17, `check_exposure.py` 16 checks,
  `check_preservation.py` pass.

## Limits of this audit

- One asset, one modifier stack, one trigger. The gap is demonstrated; its frequency is
  not measured.
- The part used for `assembly_preservation` was built from the evaluated mesh in the same
  process, standing in for a split/apply step. That is a faithful model of "the split took
  the collapsed source", but it is not a run of the project's actual split tooling.
- No visual review, no capture, no art judgement. Nothing here says the C1 state is or is
  not acceptable geometry — only that the helper set does not report the change.
- The prefix `Pilot` objects used for the synthetic empty case exist only in the
  disposable copy's memory and were never saved.

## Evidence

`.dev-shots/retention-pilot-01/`

- `retention_probe.py` — the audit probe (existing helpers, run-01)
- `run-01/result.json` — full record for C0/C1/C2 plus the synthetic case
- `run-01/assembly-C0_baseline.json`, `assembly-C1_roof_up_0p02Z.json`,
  `assembly-C2_restored.json`, `assembly-synthetic-empty.json` — the assembly documents
  handed to the helper
- `snapshot_two_states.py`, `run-02/before.json`, `run-02/after.json`,
  `run-02/policy-round61.json`, `run-02/report-01.json`, `run-02/control-identical.json` —
  the new helper's real-asset pilot
- `work/pilot_input_copy.blend` — the disposable copy, hash-matched to the round61 input
- `run-01.log`, `run-02.log` — Blender stdout/stderr, exit 0
