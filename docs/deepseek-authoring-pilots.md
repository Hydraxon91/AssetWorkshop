# DeepSeek image/text authoring pilot record

Model requested by user: OpenCode Go `deepseek-v4.1-flash#low`.
These are capability trials, not production assets or general reliability proof.

## Image-to-3D barrel

Fresh construction from five allowlisted source renders, not decimation/import
of the dataset barrel. Image-only input compliance is the worker's recorded
procedural boundary, not an enforced filesystem sandbox.

User approved corrected clay shape. Saved shape:
`.dev-shots/barrel-img2-01/shape-review-01/barrel_shape_01.blend`.
Material candidate:
`.dev-shots/barrel-img2-01/material-review-01/barrel_material_02.blend`.
Parent independently reopened both: geometry, transforms, non-lid UVs and recorded
profile/Screw controls match; source/checkpoint file bytes preserved. 7,676 triangles.
Evidence: `parent_verification_01.json` in the material-review directory.

Generated maps are mathematical NumPy patterns, not ComfyUI output or copied
dataset maps. Three 1024 maps, two model materials, reported packed maps 1,157,134
bytes. UV-only lid mapping change allowed by the material brief. Parent inspected
`material_sheet_final_03.png`: plank seams are visible, but grain is too regularly
striped, colour too dark/warm, knots weak and metal too dark/mirror-like compared
with the source. No material/user appearance acceptance is claimed.

### Tool/workflow lessons

- Validate reference subject bounds before constructing proportions. An incorrect
  height box caused a stumpy first result; fixing geometry against a wrong frame
  would obscure rather than resolve the issue.
- Enforce explicit shape-only handoff before appearance work. User requested this
  after the earlier brief incorrectly permitted both in the same correction pass.
- Procedural PBR file generation is not evidence of convincing plank materials.
  Inspect grain orientation, irregularity, seams, normal response and lid mapping.
- Check camera image-up versus model-up before expensive renders. An inverted
  three-quarter view and un-cleared clay override both weakened early evidence.
- Step-ceiling handoffs repeatedly left unfinished reporting/evidence. Preserve
  checkpoint early, reserve steps, and distinguish artifact completion from full
  task completion. No silent model substitution was used to finish the pilot.

## Next: text-only radio

User previously requested an image trial followed by a text-to-3D trial. Use a
fresh worker and empty scene, text prompt only, no earlier images/meshes/textures.
First gate is editable geometry with clay evidence; no texture generation until
independent shape review. Record limitations instead of silently repairing by a
different model. Live Blender remains untouched; isolated processes only.

### First radio result and independent finding

`text2-3d-radio-01/radio_shape_01.blend` contains new scripted construction with
an editable enclosure cage/live bevel, separate speaker bezel/face, display frame/
screen, two knob assemblies and four feet. Parent independently inspected the v3
sheet including underside and reopened the saved file: **4,654 evaluated triangles,
one material, zero images**, source bytes preserved.

The polished render did not establish the requested recesses. Parent centre-ray
tests toward both `Speaker_Face` and `Display_Screen_Recess` first hit the solid
`Body_Enclosure` wall at y≈−0.19. Intended faces exist behind it but are occluded.
Worker bounds checks marked the recesses present without testing exposure.
Evidence: `.dev-shots/text2-3d-radio-01/parent_verification_01.json`.

**New improvement opportunity:** distinguish part existence, relative depth and
visible/exposed functional surface in feature verification. A signed offset or
object name alone cannot pass a recess/opening criterion. Targeted visibility
rays support this check but do not prove every point is clear or certify motion.
No production helper changed as part of this finding.

One allowed local shape correction completed with the same DeepSeek model:
`correction-01/radio_shape_02.blend` adds two editable blind front pockets.
Parent independently reopened it, reproduced **4,894 evaluated triangles**, and
verified 10/10 centre/offset rays hit the actual speaker/screen instead of the
enclosure. Saved source bytes remain unchanged. Parent inspected the corrected
front/three-quarter sheet. This supports exposure at sampled locations, not full
intersection, manufacturing or functional certification. Detailed worker protected-
part/control comparisons remain worker evidence unless independently reproduced.

Parent completed independent shape review at the user's request:
`correction-01/PARENT_SHAPE_REVIEW.md`. Verdict: passes the bounded prompt and is
suitable for the materials stage. All 15 authored parts/poses preserved, case
proportions 1:.62:.38 verified, each evaluated part passes scoped manifold/zero-area/
loose-vertex checks. This is not production certification or user acceptance.
No appearance work started; a separate materials instruction is still required.
Shape-01 remains a preserved incomplete baseline, not retroactively accepted.
