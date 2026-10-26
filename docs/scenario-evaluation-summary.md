# Scenario collection evaluation — research complete

## Outcome

Evaluated **29 requested output examples**: original ten, thirteen additional
representatives, and six editing tasks with their source baselines. Acquisition
and inspection depth vary; this is not 29 certified production assets or a fair
generator leaderboard. Native and GLB files count as formats of one example, not
extra examples. Source baselines are separate from requested outputs.

Conservative recorded transfers: **799,174,257 bytes**, under the approved
5,000,000,000-byte cap. Pinned dataset revision:
`55b4c002b4c1529fc48da3dff98516c3069bfa3f`; CC BY 4.0, credit Scenario.
Initial pilot 7 payloads + original-seven batch 16 + expanded batch 43 = 66
payload files. Expanded payload byte/hash checks and raw geometry counts were
independently reproduced, not accepted from the worker's summary alone.

No repairs, optimization, bake, material generation, add-on installation,
production helper implementation, source saves or destination integration.
Live Blender was not used. All workers and their owned processes stopped.

## Highest-value tool improvements to implement later

| Priority | Improvement | Why this research supports it | Minimum test |
|---|---|---|---|
| 1 | Task-aware preservation checker | Retexture, roof UV, canopy and tracks provide real protected-part/source-output cases | Exact native geometry/UV/matrices, scoped allowed changes, separate export correspondence |
| 2 | Geometry + material cost report | Dense broad surfaces, repeated hardware, shared wheels and large texture/material sets | Unique/active-instance/evaluated counts, per-part costs, unique image budget, no implied GPU benchmark |
| 3 | Source/import/export preflight | Repeated-index triangles can disappear on import; S2 image MIME is wrong | Raw primitive decode, import delta categories, embedded signature/dependency checks |
| 4 | Readable comparison capture | Full wire overlays hid contours; view names and segmentation assumptions misled review | Reference/clay/flat overlay, explicit axes, camera/pixel mapping and mask inspection |
| 5 | Representation/detail-allocation sheet | Maps can replace shallow detail, not functional depth or silhouette | Geometry/normal/bump/decal/card/instance choice with distance, motion and shading tradeoffs |
| 6 | Safe bake/atlas fixtures | Verdant exposes useful dilation/instancing patterns and isolation/restoration risks | Disposable scene, explicit target set, tile-edge/mip tests, failure cleanup and normal-space fixtures |

These are scoped implementation candidates, **not already delivered tool changes**.
Some capabilities may already exist in experimental pipeline helpers; inspect and
test those before adding duplicate tools. Scratch scripts prove findings, not
production API design or general robustness. Do not import arbitrary dataset
assets into a permanent test suite without agreeing fixture size/licensing.

## What actually worked

- Independently verified retexture preserved source geometry, UVs and transforms.
  Saved appearance sheet shows blue porcelain-like finish with pale marks/bands;
  fine motif quality and exact palette are not certified.
- Native roof edit preserves all 17 mesh objects and changes only roof UVs.
  Texture scale/slope quality remains limited at reviewed image resolution.
- Canopy halves exactly, 720→360 triangles, preserving the 197-triangle trunk.
  Two opposed views reveal changed facets and lobe contours: numerical success
  is not identical appearance.
- Tracks add nonempty bands while retaining existing asset geometry/transforms.
  Visible wrapping is established, not full suspension/trajectory clearance.
- Lid animation has a visible raised keyframe gap and rim cavity cues. It costs
  about 6.5× the source triangles; protected rebuilt-body correspondence is unresolved.
- Cactus edit visibly exposes roots/layers/pot cut faces and a displaced section.
  Exact cactus/flower preservation is reported; exact cut angle and remaining
  pot/wall correspondence remain unresolved. Triangle cost grows about 4.2×.

## Efficiency and art-direction conclusions

Do not imitate dense reconstruction as the authoring standard. A 484k-triangle
toy plane, 1.49M-triangle sports car, 500k-triangle shop and 103k-triangle backpack
are useful stress fixtures, not justified target budgets. Comparisons with lighter
assets are not equal-quality benchmarks: subjects, shapes and methods differ.

Use geometry for major contour, true openings, depth/parallax that matters, moving
interfaces and close-view hardware. Investigate maps/decals for grain, shallow
grooves, paint/labels, stitching, wear, fastener impressions and lens microdetail.
Do not claim untested savings. Normal maps, material changes, decals and alpha
cards have shader/memory/overdraw costs; displacement can add geometry; instances
save source storage but do not inherently eliminate rendered triangles.

Glossy teal/yellow robots are relevant Aero-adjacent consumer-form/material studies.
Nature, small buildings and household forms broaden the sample. The bottle is
opaque, not a validated glass fixture. Generic cars do not establish RC mechanics.
Clean rounded forms with controlled gloss deserve deliberate construction, not
unnecessary surface noise. No complete Frutiger Aero style recipe is validated.

Existing StableMaterials/Qwen documentation and runners should be reused as
research context rather than duplicated. The user's ComfyUI PC is powered off;
no contact or generation was attempted. Tileable PBR generation is not automatic
object-specific sculpt baking or a substitute for geometry preservation.

## Helper code and Verdant

The dataset's pinned 3,699-file listing contains no standalone Python/JS/TS/shell
scripts or notebooks. Two original native files and sixteen additional native
source/output files report no text blocks or mesh modifiers. This does not establish
the contents of every native file in the collection. Separated objects, material
graphs and one animated lid remain editable, but construction history is absent
from the inspected cases.

Verdant was researched statically in a separate subagent, with selected mechanisms
independently checked by the parent. Useful design ideas include attribute-carried
instancing, semantic LODs and tile-local RGB dilation. Active-scene baking,
incomplete settings restoration and globally shared lookup state require caution.
No add-on execution, code copying or runtime/export validation occurred. Declared
GPL-3.0-or-later and bundled asset provenance require separately scoped reuse review.

## Remaining failed, blocked and unverified criteria

- **Failed diagnostic:** three PNGs were mistakenly dispatched to the GLB importer.
  Failures are retained; model inspections did not silently pass those image checks.
- **Metadata/reference limits:** dataset-server failures/rate limits blocked some
  source-image associations and pinned row decoding. Pinned file hashes/sizes are
  verified; provisional prompt/model labels are not independently proven metadata.
  Three original references were recovered; new thirteen and diving-helmet image
  authority remains incomplete. Supplier previews are not source references.
- **Likeness:** only helmet pilot has registered nonmetric reference-plane evidence;
  approximate projection prevents quantitative ranking. Other views are inspection
  evidence, not reference-faithful acceptance.
- **Import differences:** two expanded cars lose two/one triangles on import; cause
  remains undiagnosed. No claim of visible-area loss. GLB roof correspondence is
  also unresolved despite native preservation.
- **Structure/performance:** physical dimensions, exact interiors/wall continuity,
  full collision/clearance, all-side canopy retention, rigs, render performance,
  target-loader material fidelity and destination readiness are unverified.
- **Original seven:** technical counts and hashes independently checked; worker
  supplier-preview review is not full reference or structural verification.
- **Acceptance:** no individual asset, generator, addon or production workflow is
  accepted on the user's behalf.

## Evidence and changed documentation

- `docs/scenario-dataset-findings.md`: progressive findings F01–F17.
- `docs/verdant-research-findings.md`: external-code design findings with review status.
- `.dev-shots/scenario-eval/helmet-pilot-01/`: original pilot, independent checks,
  three editable normalized comparison checkpoints and saved overlays.
- `.dev-shots/scenario-eval/original-seven-01/`: acquisition, technical triage,
  independent payload/raw-count verification.
- `.dev-shots/scenario-eval/expanded-shortlist-01/`: provisional acquisition rationale.
- `.dev-shots/scenario-eval/expanded-acquisition-01/`: pinned payloads, manifests,
  independent byte/hash and raw-count verification.
- `.dev-shots/scenario-eval/expanded-inspection-01/`: native/GLB inventories,
  task comparisons, independent four-task preservation verification.
- `.dev-shots/scenario-eval/visual-evidence-01/`: six task sheets, two candidate grids,
  exact camera/frame mappings and worker preservation record; parent inspected all eight.
- `.dev-shots/verdant-research-01/report.md`: detailed static source citations.

The parent also changed `.opencode/agents/modeller.md` at user request: Blender
executable shell arguments are permitted while unrelated shell stays denied;
explicitly approved bounded resource acquisition is supported. Blender Python is
not sandboxed by that allowance; procedural ownership/scope restrictions remain.

**Research finished and stopped.** Next action is an approved bounded helper
implementation/test stage, not further automatic downloads or asset modifications.
