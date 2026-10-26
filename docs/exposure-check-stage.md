# Sampled exposure check — implementation stage

## Approved scope

User approved, 2026-10-25: record the improvement plan, add a narrowly scoped
sampled-exposure helper with pure and Blender fixtures, and independently reproduce
the historical radio result. No asset geometry, materials, UVs, exports, approval
records or pipeline gates change. No live Blender scene is opened or saved; fixture and
pilot runs use isolated factory-startup processes. No dependencies are added.

Step 1 of the plan (the decision-loop pilot) and step 3 (conditional
evaluated-retention extension) are **not** part of this stage. Step 1 belongs to the
next separately authorised modelling pass on the active asset. Step 3 is an audit that
must first demonstrate a gap; see "Deferred follow-up" below.

## Audit and design boundary

The failure this addresses is a check passing on a proxy while the intended surface is
not the thing a viewer actually sees. Recorded example: radio `radio_shape_01.blend`
had `Speaker_Face` and `Display_Screen_Recess` present, correctly offset and inside
their bounds, but a centre ray from the front hit `Body_Enclosure` first
(`.dev-shots/text2-3d-radio-01/parent_verification_01.json`).

Existing helpers were inspected before adding anything:

- `pipeline/preservation.py` compares **authored representation** between snapshots
  (exact geometry/UV/transform/material/image field hashes). It answers "did a
  protected field change", not "can the surface be seen".
- `pipeline/check.py:assembly_preservation` compares evaluated source point sets to
  split output parts with bidirectional distances. It answers "did the parts survive",
  not "is the part exposed".
- `scripts/check_interface.py` samples mesh-to-mesh interface distance. Contact and
  exposure are separate questions and neither implies the other.
- `scripts/check_shape_gate.py` covers bounds, hinges, modifiers and scene hygiene.

A single centre ray, as used in the radio verification, is known to be insufficient.
This helper samples a declared approach direction across the target's evaluated
triangles and reports first-hit object per sample.

## Design

Policy (`version: 1`) is an explicit `targets` list. Each rule supplies `object` and
`approach` (the world direction the viewer looks **along**; the ray origin is placed
`backoff` behind the sample point). Optional fields: `occluders` (default `"any"`,
or an exact name list), `samples` (default 16), `required_fraction` (default 1.0),
`ignore_self` (default true), `require_front_facing` (default false), `sample_facing`
(default `"target"`; `"all"` also allowed) and `backoff`.

- Samples are the evaluated loop-triangle centroids, chosen by a fixed index stride so
  the set is deterministic. World-space points and normals come from the evaluated
  object, so modifiers and transforms are respected.
- `sample_facing: "target"` samples only triangles presenting to the viewer; a closed
  part's rear and side faces are excluded because asking whether they are visible is not
  an exposure question. `"all"` keeps every triangle for deliberate diagnostics.
  Each sample records its own `target_facing` so the choice is auditable.
- Sample status is `visible`, `blocked`, `miss` or `error`. A non-target first hit is
  `blocked` and records the blocker. A hit outside an explicit `occluders` list is
  flagged `unexpected_blocker` rather than silently accepted.
- Rule status is `pass`, `fail` or `error`. `miss` and `error` samples make the rule
  `error` (inconclusive), never a pass. Zero samples is `error`.
- `require_front_facing` (off by default) turns a `visible` sample into `blocked` when
  the surface actually hit faces away from the viewer, catching inverted normals. It is
  off by default because interior and recess surfaces legitimately face the cavity.

Not claimed: transparency (a pane blocks a ray), complete surface coverage, recess
depth, clearance, collision, likeness, or user acceptance. Helper output is evidence,
not a delivery gate. Promotion of this helper to a blocking stage check requires
separate approval after its coverage is demonstrated.

## Verification plan

1. Pure policy and summary tests: defaults, malformed input rejection, missing/duplicate
   targets, zero-length approach, invalid sample counts and fractions, unexpected
   blockers, zero-sample and miss handling. No Blender required.
2. Disposable Blender fixture: exposed, fully blocked, half blocked, and visible through
   a frame opening (recess analogue); modifier-generated occlusion; a transformed
   target; an explicit-occluder mismatch; a missing target; a target with no faces.
   Assert unrelated data, selection, frame and active object are unchanged.
3. Independently reproduce the historical radio pair: `radio_shape_01.blend` must report
   blocked samples, `correction-01/radio_shape_02.blend` must report visible samples.
   Historical reports are expected results to test against, not proof.
4. Re-run the existing preservation and pipeline pure regressions to confirm nothing
   else changed.

Source `.blend` bytes must be unchanged after every pilot run.

## Status

Implementation complete; results recorded below.

- `pipeline/exposure.py` — policy validation, sample summary and evaluated sampling.
- `scripts/check_exposure.py` — CLI; exit 0 pass, 1 fail, 2 invalid input/output;
  refuses to overwrite.
- `fixtures/test_exposure.py` — 17 pure tests.
- `fixtures/check_exposure.py` — disposable Blender regression, 16 named checks.

### Verification results

- Pure: `python tools/asset-pipeline/fixtures/test_exposure.py` — **17 passed**.
- Existing regressions re-run, unchanged: `fixtures/test_preservation.py` **12 passed**,
  `fixtures/test_pipeline.py` **12 passed**.
- Blender: `fixtures/check_exposure.py` passes all 16 checks with exit 0, and asserts
  that neither unrelated mesh data nor its own targets were mutated, and that frame,
  selection and active object were unchanged.
- Pilot (Blender 5.2.3 LTS, `--background --factory-startup --disable-autoexec`):

| File | SHA-256 (first 16) | Speaker_Face | Display_Screen_Recess | Source bytes |
| --- | --- | --- | --- | --- |
| `radio_shape_01.blend` | `b5d342967a806488` | fail, 0/16, `Body_Enclosure`×16 | fail, 0/16, `Body_Enclosure`×16 | unchanged |
| `correction-01/radio_shape_02.blend` | `d99ef67a8df702c1` | pass, 16/16 | pass, 16/16 | unchanged |

The recorded historical probe was one centre ray per target; this reproduces the same
first-hit object with 16 samples per target and extends the claim to the whole sampled
surface. It does not establish that every point is clear.

### Findings and corrections during the stage

1. **Unfiltered sampling invented failures.** The first pilot run reported
   `Display_Screen_Recess` as 13/16 visible, three samples blocked by `Body_Enclosure` at
   `y = -0.140` while the sample points sat at `y ≈ -0.1648`. Those samples were rear
   faces of the closed recess box, which sit behind the enclosure front by construction.
   Asking whether the back of a pocket is visible from the front is not an exposure
   question. `sample_facing` (`target` default, `all` available) now samples only
   triangles presenting to the viewer, and each sample records its own `target_facing`
   value so the choice is auditable. The control run with `sample_facing: "all"`
   deterministically reproduces the original 13/16, and the fixture proves that a surface
   facing away is reported as `error`, not as a pass.
   This default changed **after** observing the 13/16 result. It is not a threshold
   relaxed to obtain a pass: the excluded triangles face away by construction, the
   original measurement is preserved as run-01 and as a reproducible control, and the
   rule is stated in the policy and the module limits.
2. **Fixture sample counts derive from triangles, not quads.** The first Blender fixture
   run failed because an 8-triangle plate yields 8 samples, not the 4 quad centres
   assumed. The fixture expectation was corrected; the helper was not.
3. **The read-only assertion initially compared the wrong sets.** The fixture compared a
   pre-creation snapshot of unrelated objects against a post-creation snapshot of every
   mesh, so it failed for a reason unrelated to mutation. It now compares the non-fixture
   and fixture sets separately.
4. Limits confirmed by construction: transparency is not modelled, sample count bounds
   coverage rather than certifying it, and clearance/contact/likeness remain separate
   checks.

Evidence: `.dev-shots/exposure-pilot-01/run-03-final/` (final reports, policy, logs).
`run-01/` (unfiltered first draft) and `run-02/` (filtered, before `target_facing` was
recorded) are retained as superseded drafts, not as current results.

A post-refactor confirmation run reproduced both files' target classifications exactly
(`shape01` fail 0/16 blocked by `Body_Enclosure`; `shape02` pass 16/16).

### Live-session check (read-only)

Run inside the live Blender session through the MCP addon, on the open checkpoint
`seat_01_stage2b_02.blend` (clean, 18 objects), using `cam_01_front_negY`'s actual view
direction `(0, 1, 0)` rather than a hand-written axis:

| Target | Visible | Blockers |
| --- | --- | --- |
| `seat01_squab` | 16/16 | none |
| `seat01_backrest_shell` | 11/16 | `seat01_squab` ×4, `seat01_piping` ×1 |

Objects, mesh vertex/polygon counts, selection, active object, frame and the dirty flag
were all unchanged, and no file was written. This confirms the helper works in the live
MCP session, not only in `--background`.

**Finding:** the default `required_fraction: 1.0` reports ordinary occlusion as `fail`.
A part legitimately sitting behind another cannot pass that default; the fraction must
come from the intended view, or the expected occluders should be named. The backrest
result above is expected seat geometry, not a defect — no art judgement was made and no
criterion was invented for the active asset.

#### Junction camera blocker map (`cam_05_junction_left`)

`BLENDER_OWNER.md` records the open requirement for this stage as closing the seam line
of sight. That is an exposure-shaped question, so it was run read-only against
`cam_05_junction_left` (location `(-0.36, -0.2, 0.74)`, view direction
`(0.445245, 0.890489, -0.093736)`), 16 samples per target, on the same checkpoint
(`sha256 019774227c6ebc76…`, clean before and after).

| Target | Visible | Blocked | Miss | Blocker |
| --- | --- | --- | --- | --- |
| `seat01_backrest_shell` | 15/16 | 1/16 | 0/16 | `seat01_piping` at `(-0.08174, 0.22045, 1.06913)` |
| `seat01_squab` | 16/16 | 0/16 | 0/16 | — |

`required_fraction` was set to `0.0` for this run. No criterion for this asset has been
agreed, so the helper's pass/fail verdict was neutralised rather than manufactured; the
output is a blocker map, not an acceptance result.

What the map says: every sample taken on those two surfaces was reachable from this
camera, and one backrest sample was reached through the piping. No sample escaped.

**Correction (superseding the interpretation first reported):** this does **not** show the
junction reads closed. The helper samples *points on the target surfaces* and asks whether
the target is the first thing hit along that point's approach. It never aims a ray *through
the seam* into the cavity, so it cannot detect whether a gap exposes the interior. A zero
`miss` count here means "the sampled surface was not buried", not "there is no line of
sight through the joint". The earlier statement that the junction "reads closed from this
camera" was an over-reading and is withdrawn.

The seam question therefore remains open and needs a matched render at a view that
actually contains the joint. Saved `cam_05`/`cam_06` do not frame it; the proven intake
temporary-view framing does. Sixteen surface samples also cannot see a ~2 mm gap, and no
art criterion was invented for this asset.

`cam_06_junction_right` was conditional on this camera being uninformative. It appeared
informative, so no second camera was run. Given the correction above, a right-side map
would not answer the seam question either; it maps the same surface-visibility property
from the other side.

Evidence: `.dev-shots/exposure-pilot-01/seat-cam05/report-01.json` and `meta-01.json`
(checkpoint path, SHA-256, camera transform, policy, `state_unchanged: true`,
`scene_saved: false`).

The run used the then-current `seat_01_stage2b_02.blend`
(`sha256 019774227c6ebc76…`). The preserved intake is now
`seat_01_junction_intake_01.blend` (`a2512545…`), whose geometry was verified identical
to that baseline; this map was not re-run and its numbers belong to the earlier file.

## Evaluated retention — separate follow-up

Evaluated-retention (did an edit remove most of the evaluated body while leaving healthy
sources) is a separate question from exposure and from exact authored preservation. It is
**not** part of this stage and none of the exposure code answers it.

The audit this stage deferred has since been run: `docs/evaluated-retention-audit.md`
reproduces the round61 disappearing-body case on a disposable copy and records that
`mesh_health` and `assembly_preservation` both report `ok` on a state where 81.8% of the
evaluated vertices are gone. The proposed extension there is a proposal only; nothing was
implemented, and it still needs approval.
