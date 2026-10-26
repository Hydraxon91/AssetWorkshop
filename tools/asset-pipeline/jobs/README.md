# Historical jobs — archival, not ready-to-run assets

All 33 original top-level `*.job.json` files are preserved unchanged.
Audit them from the workspace root:

```sh
python3 -B tools/asset-pipeline/scripts/audit_historical_jobs.py
```

Current disposition:

- **31 archival-blocked:** all jobs other than the two listed below declare missing
  laptop, mug or deskfan `.blend` sources. `deskfan-hybrid-overrides.job.json` also
  requires three missing corrected material maps. These are absent asset histories,
  not paths that can be safely fixed by substituting the watering can.
- **2 archival-requires-explicit-scene:** `laptop-atlas.job.json` and
  `laptop-atlas-smoke.job.json` omit `source` and depend on an already loaded scene
  containing `Shell_Root`. Neither is approved to operate on the live scene.

No corrected runnable copies were created: no corresponding local asset sources
were found at the declared paths. Do not fabricate paths, use similarly named
unverified files, or run these jobs unchanged. If sources are separately migrated,
make new-name jobs with explicit sources and fresh output paths, preserve originals,
and validate object/material identities and embedded dependencies before execution.

The path audit checks source/GLB inputs, gates, tile-base inputs and output locality.
It does not inspect `.blend` internals, validate job verbs or certify output safety,
geometry, exports or destination compatibility. It never probes external repositories.

## Material examples

The seven jobs in `../examples/` are a separate runner format, not pipeline jobs.
Their template paths resolve locally. StableMaterials deskfan-v4 dry-run previously
passed. The laptop Qwen job requires historical UV/reference images not bundled as
part of the current watering-can sources; treat it as archival until supplied.
Other StableMaterials examples are reusable prompt candidates, not accepted asset
materials. Live ComfyUI testing is **DEFERRED**; no server/generation checks are
implied by offline graph preparation.
