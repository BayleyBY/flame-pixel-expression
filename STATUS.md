# Project status

*Hand-maintained dashboard — update alongside CLAUDE.md/README on library changes
(`/sync-docs` does not manage this file). Last updated: **2026-07-23**.*

## Library

| Bucket | Count | State |
|---|---|---|
| `setups/Uploaded to Logik-Portal/` | 112 | Verified in Flame 2027.1, published to the Logik Portal |
| `setups/WORK IN PROGRESS/` | 45 | Held back; every `.md` has a "### Quick test" recipe |
| `setups/_READY_FOR_LOGIK/` | 1 | `hsv_color/hsv_grade` — Flame-verified 2026-07-23, staged for next Portal upload |
| **Total** | **158** | Validator: 0 errors / 0 warnings · glslangValidator: all compile |

## Pending verification / attention

- ⚠ **`channel_pack` / `channel_unpack`** — widened to 4 channels 2026-07-23 (ch4 = Front 2
  luma on OutMatte; unpack `pick` 3 = m1). **Not yet re-verified in Flame**; Quick tests in
  their `.md`s. Portal still has the 3-wide versions until the user re-uploads.
- ⚠ **`radial_ramp`, `palette_quantize`** (WORK IN PROGRESS) — 2026-07-21 bug-fixes never
  eyeballed in Flame; their Quick tests flag exactly what to confirm.
- **Next Portal batch** (user's call): the 4-wide pair update + `hsv_grade`.

## 2026-07-23 session log

- `despill_blue` — user built in Flame from `despill_green`; integrated into the generator,
  regenerated in place in `Uploaded to Logik-Portal/color_grade/` (verified, published).
- `hsv_grade` — new HSV-sandwich grade (`rgb_to_hsv` → it → `hsv_to_rgb`): wrapping
  `hueShift`, `satGain`/`satGamma`, `valGain`/`valGamma`. Verified in Flame; staged.
- `channel_pack`/`channel_unpack` widened to 4 channels (see above).
- `demo_images/` added — test assets (see below). EXR gitignored (87 MB, regenerable).
- Doc lessons from the user's live STMap tests: **32-bit-float maps end-to-end** (16f
  quantizes UV → soft results), **prefer Transform for affine moves** (STMap sampler is
  bilinear), **CA needs the per-channel workflow** (one map = uniform zoom). Shared
  `_STMAP_NOTE` on all 11 UV-map emitters + `node_dependencies.md` checklist points 5/6.

## Demo assets (`demo_images/`)

- `aov_demo_render.exr` — synthetic CG render, 18 layers/38 channels: beauty, albedo,
  diffuse + **direct/indirect(unoccluded) split**, specular, over-range emission, AO, N, P,
  depth.Z, screen-space velocity, real 2-rank Cryptomatte (MurmurHash3 ids + manifest).
  Feeds every data-consuming setup; ids + scene ground truth in `aov_demo_manifest.txt`.
- Beauty rebuilds proven: baked path exact (4.3e-7); three-way split w/ `ao_multiply` exact
  off edges (comp-side AO's filtered-product limitation — 0.12% edge pixels, max 2e-2).
- `stmap_demos/` — map + expected-result reference pairs for all 10 ST-map generators
  (exact GLSL math, bilinear STMap simulation), `arch_base.png` + `uv_test_chart` sources,
  squeezed anamorphic source, CoC previews from the EXR's real depth.
- Comparisons: `hue_preserving_clip_demo.png`, `screen_merge_demo.png`, contact sheets.

## Standing facts

- Repo public: `github.com/BayleyBY/flame-pixel-expression` — push to `origin main` normally.
- Golden rule: `tools/generate_setups.py` is the single source of truth; never hand-edit
  generated files. Routine loop: edit generator → regenerate → validate → compile-check →
  doc sync (`/sync-docs`) → commit/push.
- Layout is the user's hand-managed publication state; generator regenerates in place.
- The node cannot gather (no neighbour sampling, no warping/blur in-node) — map generators
  always pair with a downstream STMap/Defocus.
