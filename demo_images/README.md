# demo_images — test assets for the Pixel Expression library

Untracked working assets (2026-07-23). The EXR is 87 MB — do **not** commit it.

| File | What it is |
|------|------------|
| `aov_demo_render.exr` | Synthetic CG render, 1920×1080, 18 layers / 38 channels (all float32, ZIP). Exercises every data-consuming setup in the library. |
| `aov_demo_manifest.txt` | Cryptomatte float32 ids + full scene ground truth (camera, sphere centres/radii — the values to type into `pmatte_sphere` etc.). |
| `render_aov_exr.py` | The generator — analytic numpy ray-tracer, reproducible/tweakable. Needs `pip install OpenEXR`. |
| `aov_contact_sheet.png` | All layers visualised for eyeballing. |
| `screen_merge_demo.png` | `screen_merge` vs plain add on the emission glow (zoom inset on the halo edge). |
| `neon_base.png` / `hue_preserving_clip_demo.png` | Nano Banana neon night scene + naive-clip vs `hue_preserving_clip` comparison. |

## EXR layers → which setups they feed

| Layer | Feeds |
|---|---|
| `RGBA` beauty | reference for rebuilds; alpha is 16×-supersampled |
| `albedo`, `AO` | `albedo_divide`/`albedo_multiply`, `ao_multiply` |
| `diffuse` (AO baked in) | legacy/compat two-node rebuild below |
| `diffuse_direct` | sun × traced shadows — AO plays no part, by construction |
| `diffuse_indirect` | **unoccluded** ambient ("diffuse without AO") — multiply AO in comp |
| `specular`, `emission` | `aov_add`, `aov_grade_add`, `screen_merge` (emission peaks at 5.6 — over-range on purpose) |
| `N.X/Y/Z` (−1..1, unit) | `normal_relight`, `fresnel_facing`, `normal_to_facing`, `normal_renormalize` |
| `P.X/Y/Z` world position | `pmatte_*`, `box_matte`, `position_range_remap` |
| `depth.Z` (sky = 1e6) | all depth tools + `coc_from_depth`/`thin_lens_coc`/`depth_dof_mask` |
| `velocity.X/Y` (screen px, ~213 px max) | `motion_vector_visualize`/`normalize` |
| `CryptoObject00` (2 ranks) | `crypto_pick_2rank` — real MurmurHash3 ids + subsample coverage + manifest metadata |

**Read the EXR Raw / no colour management, no filtering** — critical for crypto, P, N.
Data passes (P/N/Z/velocity) are unfiltered centre-samples, as real renderers deliver them.

## Beauty rebuild #1 — baked diffuse (exact everywhere)

```
diffuse ──► Front 1 ┐
                    ├ aov_add ──► Front 1 ┐
specular ─► Front 2 ┘                     ├ aov_add ──► rebuilt beauty
                          emission ─► F2  ┘
```
All defaults. Max error 4.3e-7 wherever alpha = 1 (addition commutes with pixel
filtering). The sky gradient lives only in beauty — comp the rebuild over a background
via alpha; verify with `difference_matte` (rebuild F1, beauty F2, gain 5) → black.

## Beauty rebuild #2 — three-way split (the *correct* AO placement)

```
diffuse_indirect ─► Front 1 ┐
                            ├ ao_multiply ──► F1 ┐
AO ──────────────► Matte 1 ┘  (defaults:         ├ aov_add ─► +specular ─► aov_add ─► +emission ─► aov_add ─► beauty
                               amount 1,          │
                               aoGamma 1          │
                               = straight ×)      │
                        diffuse_direct ──────► F2 ┘
```
Only the indirect branch passes through AO; `diffuse_direct` joins untouched.

**Accuracy (the lesson):** exact to 2e-5 on 99.88 % of the frame; up to 2e-2 on the
0.12 % of pixels that straddle object edges — verified to be 100 % of the error. Two
*filtered* passes multiplied (`indirect × AO`) can't equal the filtered *product* where
both vary inside a pixel. This is why path tracers ship `diffuse_indirect`
already-occluded and treat AO as a utility pass. `difference_matte` at gain 5 reads
black; at gain ~50 thin object outlines appear — the artifact to know about when
grading AO in comp on production renders.

## Naming note ("diffuse without AO")

Most pipelines just call the unoccluded pass `diffuse` — AO isn't supposed to be baked
into a lighting AOV. Explicit names in the wild: *unoccluded diffuse*, `diffuse_raw`,
`diffuse_noAO`. V-Ray's "Raw Diffuse" means the **albedo** is divided out — a different
"raw". Path tracers mostly don't have the concept: occlusion emerges inside
`diffuse_indirect`.

## Other demos from this EXR

- **`screen_merge`** (`screen_merge_demo.png`): base = `diffuse` + `specular`, glow =
  `emission` + blur (Flame: Glow/Blur node — the Pixel Expression node can't sample
  neighbours). Plain add clips 12.1 % of the frame; screen (`1−(1−base)(1−glow)`) clips
  nothing and keeps checker/shadow detail near the halo. Screen is display-referred
  0..1 math — a look operator, never for exact rebuilds.
- **Deeper diffuse split:** `albedo_divide` (diffuse F1, albedo F2) → grade the pure
  lighting (removes the floor checker) → `albedo_multiply` (albedo F1, lighting F2).
  Divide→multiply with no grade is another exact no-op.
- **Delivery clamp:** the rebuilt beauty carries the over-range emission core (5.6) —
  `hue_preserving_clip` last in the chain brings it into range without hue twist.
