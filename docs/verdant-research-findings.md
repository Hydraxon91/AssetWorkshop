# Verdant static research — design findings

Source inspected read-only at user-supplied path:
`/Users/hydraxon/Downloads/Telegram Desktop/too_many_addons/verdant-0.1.0`.
Worker report with complete line citations:
`.dev-shots/verdant-research-01/report.md`.

Static research is complete. No installation, imports, execution, Blender access,
source copying or runtime validation occurred. Manifest declares GPL-3.0-or-later;
reuse/redistribution and bundled asset provenance require separate review. Generated
outputs are not automatically classified by the add-on license alone.

## Independently checked findings

### V01 — Attribute carriers for repeated detail

Parent read `bl/organs.py:18–79`: one point per organ stores rotation, scale,
variant and random attributes with bulk setters. A node modifier instances the
source collection with Realize false by default. This suggests an efficient editable
representation for repeated foliage and small set-dressing details.

**Proposed improvement:** representation planner and repeat-detail helper that
retains instance transforms/source IDs and distinguishes stored, instantiated and
realized geometry. Node internals, actual performance and export behavior are
unverified; point-carrier storage does not prove fewer rendered triangles.
**Status:** design evidence confirmed; no helper implementation approved/performed.

### V02 — Tile-local color dilation without changing alpha

Parent read `impostor/dilate.py:25–101`: separate-tile eight-neighbor propagation
extends RGB into transparent texels while leaving alpha unchanged and avoiding
wraparound. This addresses a real class of filtering seams without adding topology.

**Proposed improvement:** atlas-edge test fixtures and an independently designed
dilation stage with per-island/tile limits; test mip levels against bright/dark
backgrounds. Do not assume four pixels suffice for every distance or atlas size.
**Status:** algorithmic behavior confirmed statically, not executed or copied.

### V03 — Bake isolation and complete failure restoration

Parent read `impostor/bake.py:136–157,198–324`: supplied objects determine bounds,
but rendering uses the active scene. The saved-state dictionary and finally block
omit changed color depth and Cycles sampling/device/denoising settings. Temporary
camera/material creation begins before the protected try block.

**Proposed improvement:** use an isolated temporary scene with explicit target
objects/world/lights, new-name output policy and injected-failure restoration tests
in any future AssetWorkshop bake helper. This is a lesson from external code,
not evidence that our current bake helper has the same defects.
**Status:** static control flow confirmed; runtime contamination/impact untested.

### V04 — Scope lookup data to each owner, not a global name

Parent read `bl/scatter.py:141–174`: `build_table` retrieves one global lookup
object and replaces its mesh. Multiple scatter surfaces may reference the same
object, so updating one can affect another's lookup.

**Proposed improvement:** stable per-owner IDs and a two-surface isolation fixture
for future scatter helpers. Name alone is not a sufficient ownership boundary.
**Status:** shared lookup mechanism confirmed; actual multi-surface regression untested.

## Additional candidate findings — worker evidence, not independently accepted

- Semantic LOD tiers prune branches and reduce ring/organ density; some dropped
  branches become untextured cards. Prefer semantic reduction over indiscriminate
  decimation when source controls exist. Shading/silhouette retention needs tests.
- Directional atlases use invariant framing; crosscard helper exists but was not
  found on a UI operator path. Neither is demonstrated portable delivery support.
- Bake color renders original shaders and lighting, so it is not established
  relightable albedo. Normal space/cutout handling needs analytic fixtures.
- Atlas default render count/memory and alpha overdraw belong in budget reports;
  cards are not automatically faster than geometry, especially in reflections/shadows.
- Full recipes, stable dependency IDs and node-interface versions are preferable
  to partial seed/settings stamps and global/name-only lookup. Deterministic random
  streams do not alone prove cross-version Geometry Nodes determinism.

## Recommended later gate

Do not install Verdant as part of dataset research. If experiments are approved,
use disposable fixtures to test representation cost, clean baking, mip edges,
rotated cutout normals, multi-owner independence and complete failure cleanup.
Keep GPL/provenance review, runtime validation, source portability and destination
integration separate. No production tool or add-on was modified by this research.
