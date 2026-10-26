# GummyBearTest delivery contract — NOT STARTED

Destination: **GummyBearTest**, confirmed by the user.

User decision (2026-10-23): the destination contract is **deferred until working
assets exist**. The earlier requirement to obtain a requirements handoff before any
manifest work is withdrawn. This is no longer a project blocker: authoring may
continue without it, and no asset work is withheld pending the contract.

Implementation still needs real destination requirements. Do not invent a schema,
infer one from guesses, or read the game repository without separate approval. The
checklist below remains the request to send when that work starts.

## Information requested from the destination owner

1. **Authoritative contract:** existing manifest/schema and validator, if any;
   contract version/identifier, required versus optional fields, and one accepted
   package example (with any credentials or private content removed).
2. **Package boundary:** required files and directory layout, asset-ID/naming rules,
   permitted relative paths and external resources, version/update rules, hash
   algorithm and exact files/bytes to hash. State whether editable Blender sources
   are required, optional or excluded from delivery.
3. **Runtime payload:** supported formats/glTF extensions, coordinate/units/origin
   conventions, root/node naming and hierarchy, animation/rig/morph requirements,
   material/alpha/texture/color-space expectations and any numeric budgets.
4. **Acceptance policy:** required export/validator checks, warning allowances,
   required visual/provenance/license/approval evidence, and unsupported-case
   behavior. Identify what must be blocked versus reported for review.
5. **Intake boundary:** exact game-side intake command/API, responsible owner,
   expected success/failure outputs and fixtures, validation-versus-install behavior,
   and the separately approved procedure for testing an actual delivered package
   in GummyBearTest without unintended asset replacement.

## Local preparation and limits

Existing local tooling includes guarded GLB export, structural inventory, clean
Blender import, pinned Khronos validator `2.0.0-dev.3.10`, and hash-linked capture/
evidence helpers. Validator provisioning and nine smoke tests passed. These are
reusable prerequisites, **not** an implemented delivery manifest/intake contract.

When work starts: map supplied requirements to a local implementation and tests;
test valid/invalid packages, path containment, missing/swapped/stale payloads and
evidence under that contract. Do not invent a provisional destination schema now.

- Versioned manifest/package validation: **DEFERRED — awaiting working assets**.
- Destination compatibility/intake: **UNVERIFIED — must be tested separately in
  GummyBearTest**. Local package validation can never establish this on its own.
- Live ComfyUI generation/service and generated-material quality: **DEFERRED**.
- No model editing, integration, dependency changes, deletions, commits or pushes.
