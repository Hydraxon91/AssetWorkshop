# Fixtures

Reusable, job-driven pipeline code lives one level up in `pipeline.py` and `pipeline/`.
This folder contains reusable **builders and regression fixtures** that the pipeline
cannot generalise. Asset-local experiments/recovery sources remain under
`.dev-shots/<asset>/scripts/`; do not promote them without demonstrated reuse.

Migration policy:

- New reusable builders/tests go here, not into `../tests/`.
- `../tests/` keeps the existing phase scripts unchanged so current checks and CI keep
  working; nothing is renamed or moved as part of this migration.
- A builder here must write to `.dev-shots/` (gitignored) or an explicit out-dir and must
  refuse to overwrite an existing checkpoint.
- Geometry construction is intentionally not parameterised into `pipeline.py`: an asset
  builder is a fixture, while inspection, UV, bake, check, render, export and verify are
  shared verbs.

Historical migration candidates (not an automatic move plan):

```text
fixtures/
  office_corner.py        from tests/phase7/build_office_corner.py
  retro_laptop.py         from tests/phase7/build_retro_laptop.py
  frutiger_props.py       from tests/phase7/build_frutiger_props.py
```

No file may be duplicated between `tests/` and `fixtures/`; move only when the old path is
retired in its own reviewed change.
