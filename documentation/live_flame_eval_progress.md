# Live-Flame evaluation — progress tracker

Working through an **in-Flame load/visual test of every setup**, one at a time. The user loads
each in Flame and approves or rejects it.

## ⚠️ RESET after the PR245 node format change (2026-07-07)
A Pixel Expression node update **changed the save-file XML** (variables → `<Variables>` list, new
`<…Declarations>` blocks, lean static channels — see `flame_pixel_expression_file_format.md`). Old
-format files no longer load, so **all prior approvals are void** and the eval restarted from **0/156**
against the updated node. The whole library was regenerated to the new format; only the file wrapper
changed (GLSL/expressions untouched), so re-verification should be quick — the previously-approved
16 in particular.

## Tracking method (CHANGED — no more approved/ subfolders)
The old approach *moved* files into `approved/`/`rejected/` subfolders, which broke regeneration
(the generator writes flat and doesn't clean, so regen resurrected duplicates → the "do not
regenerate" freeze). **Now: track status here as a checklist and leave the files flat.** This keeps
`tools/generate_setups.py` as the single source of truth and safe to re-run at any time.
- ☐ = not yet loaded · ✅ = loads + renders correctly in the updated node · ❌ = fails (note why → fix
  in `generate_setups.py`, regenerate, re-check).

## Scope / order
- **Scope:** all 156 setups (new format — none carry over from the old eval).
- **Order:** highest-risk first (heaviest GLSL, below), then the rest by category.

## Status: 96 / 156 confirmed (new format)  ·  ✅ PHASE 1 & PHASE 2 COMPLETE · ▶ Phase 3/4 (basics) underway · ⚠ 15 passes revoked by the 2026-07-21 bug-fix pass (below)

### ⚠️ Bug-fix pass (2026-07-21) — 17 setups' GLSL changed; 15 previous passes REVOKED
A full semantic review (Fable) found and fixed real rendering bugs; the offline checkers stayed
green throughout (they can't see semantic bugs — that's why these passed eval: they *loaded*
fine, they just rendered subtly-to-plainly wrong). Fixed in `generate_setups.py` + regenerated.
**Revoked (were ✅, GLSL changed — re-verify):**
- `hue_rotate`-matrix family — rotation direction was INVERTED (and 601-luma): `color_replace`
  recoloured to the wrong side of the wheel, `hsl_targeted` pushed opposite its own recipes.
  Revoked: `painted_grade` (matrix user). (`hue_rotate`/`color_replace`/`hsl_targeted` were
  still unconfirmed — fixed too.)
- `halftone` — tonality was inverted (bright areas got the big ink dots); formula `dot`→`ink`.
- `crosshatch` — polarity inverted (rendered white-on-black; docs promise black-on-white).
- `palette_quantize` / `zone_system_posterize` — top step overshot past 1.0 on clipped input.
- `sdf_rounded_box` — default hollow=0 drew a 50%-grey slit through the middle (negative inner
  extent); hole rebuilt with capped inner corner radius `cin`.
- `sdf_polygon` — `hollow` had a dead zone (up to half the slider); rebuilt on a true SDF.
- `starfield` — every star sat at its cell's top edge in rows of clipped discs (existence gate
  shared the position hash); gate now independent, positions inset.
- `kaleidoscope_map` — output was re-anchored to frame middle, ignoring a dragged Centre (again;
  this is the output side, the 2026-07-07 fix was the input side).
- `mandelbrot` / `burning_ship` — exterior had a 12.5% grey floor, never reached black.
- `radial_ramp` — softness=0 hit smoothstep(edge0==edge1), GLSL-undefined; half-pixel inset.
- `alpha_crunch` — default thresh 1.0 zeroed every non-solid matte pixel on load → 0.1.
- `dual_output_depth` — default strength 0.0 made the documented depth tint a no-op → 1.0.
- `st_uv_map_inspector` — flagged legal UV==1.0 (top/right edge of a valid map) as out-of-bounds.
**Also fixed, not previously confirmed (no revocation):** `normal_relight` (NaN guard for the
(0,0,0) normals outside geometry). **Doc-only (no re-verify needed):** `color_blindness.md`
(colour-space claim corrected to linear-RGB per Machado), `mandelbrot.md`, `starfield.md`, etc.

### ▶▶ RESUME HERE (next session) — 60 setups left (45 basics + 15 revoked above)
Confirm the remaining folders (whole-folder batches have been passing fast), then re-verify the
15 revoked bug-fix setups (their GLSL genuinely changed — eyeball the fixed behaviour, don't just
load-check). **Remaining folders:**
- `aov_tools/` (motion_vector_visualize/normalize + albedo_divide/multiply, ao_multiply, aov_add,
  aov_clamp_negative, aov_grade_add, crypto_pick_2rank/4rank, id_isolate, screen_merge)
- `3d_position_tools/` (normal_renormalize, normal_to_facing, position_range_remap + pmatte_sphere/
  rings/rays, box_matte, normal_relight, fresnel_facing)
- `depth_tools/` (depth_normalize, depth_matte, depth_dof_mask, depth_contours, depth_posterize,
  depth_fog, depth_fade, depth_mix, depth_grade — 9 files; the last two were missing from this list)
- `uv_distortion/` (all)
- `hsv_color/` (rgb_to_hsv, hsv_to_rgb, hue_rotate, chroma_key, color_replace, vibrance,
  hsl_targeted, split_tone, sat_matte)
- `utility/` (stmap, nan_cleanup — uv_test_chart already ✅)
Phase 2 done: stmap_generators, stylization, optics_physics, control_surfaces, sdf_shapes,
pattern_generators, diagnostics. Phase 3/4 folders confirmed by whole-folder batch:
- ✅ **`color_grade/` (20)** confirmed 2026-07-07 (log-curve round-trip pairs, grades, cosine_palette,
  lens_vignette, voxelize).
- ✅ **`matte_combine/` (11)** confirmed 2026-07-07 (set ops, premult/unpremult, holdout, screen/mult,
  falloff). **matte_grade: added `lift`** (now lift/gamma/gain matching lift_gamma_gain) — reload to
  confirm.
- **`alpha_matte_tools/` (6)** confirmed 2026-07-07 — ⚠ **alpha_crunch REVOKED 2026-07-21**
  (default `thresh` changed 1.0 → 0.1; fill_alpha, alpha_fringe, luma_key, difference_matte,
  garbage_gradient_matte stay ✅).
- ✅ **`animated_generators/` (9)** confirmed 2026-07-07 (wave_sine/triangle/square/sawtooth/bounce/
  blip/parabolic + pulse_rings, spin_rays — animated `t` motion confirmed).
- **`sdf_shapes/` (8)** confirmed 2026-07-07 — ⚠ **sdf_polygon + sdf_rounded_box REVOKED
  2026-07-21** (bug-fix pass; the other 6 — sdf_lattice, smin_metaballs, metaball_ring, sdf_box,
  sdf_circle, sdf_ring — stay ✅).
- **`pattern_generators/` (16)** confirmed 2026-07-07 — ⚠ **radial_ramp + starfield REVOKED
  2026-07-21** (bug-fix pass; the other 14 stay ✅: wood_grain, marble, triangle_tiling,
  log_polar_spiral, point_grid, zone_plate, bricks, checkerboard, noise_random, rays, rings,
  hex_grid, truchet, wave_interference).

### ⚠️ Centre-convention fix (2026-07-07) — 4 stmap setups re-opened
PR245 defaults Centre to the image middle. Four ST-map setups did their OWN `-0.5` centering and
treated `centre` as an *offset from middle* (`(x+0.5)/width - 0.5 - centre.x/width`), so the new
middle default double-shifted their pole/optical-centre into the corner. Fixed to use `centre` as
an **absolute pole** (like `radial_ramp`): `((x + 0.5 - centre.x) / width)`, and dropped the now-
wrong `0.5 +` origin in the lens/chromatic output. Affected: `polar_to_cartesian`, `kaleidoscope_map`,
`lens_distort_map`, `chromatic_aberration_map` — the last 3 were "passed" mis-centered (not obvious
as abstract maps), so their passes were revoked and **re-confirmed in the Phase-2 folder pass**
(the ✅s in the Phase-2 list below are the post-fix re-checks). Note `kaleidoscope_map` was
re-revoked 2026-07-21 for a separate output-side bug. Lesson: any setup that normalizes coords
itself and subtracts a normalized `centre` needs this treatment.
Library is now **156** (added `metaball_ring`). Animated channel (thin_film `shift`, metaball_ring
`spin`) confirmed live.
- ✅ **entire `noise/` folder (7)** confirmed 2026-07-07: voronoi_edges, voronoi_manhattan,
  voronoi_chebyshev (Phase 1) + voronoi, noise_value, noise_fbm, noise_cells (Phase 4).

### New setups added during the eval (net-new, not from the old 155)
- ✅ `sdf_shapes/metaball_ring` — 6 blobs on a ring (smooth-min welded), `spin` rotates. Built +
  confirmed 2026-07-07 as the higher-count companion to `smin_metaballs` (which caps at 3 for the
  8-var budget). File 4.4 KB, well within the expression-length limit.
- ⚠ `pattern_generators/radial_ramp` — confirmed during the PR245 fix (loads, 8 vars + `dist`
  formula present, glow centred at image middle, radius pixel-accurate); **REVOKED 2026-07-21**
  (softness=0 smoothstep fix — re-verify).
- ✅ `stylization/digital_counter` — 2026-07-07; loads + renders a clean digit at Centre (the
  library's longest expression). **Renamed from `seven_segment`** at the user's request.

### ▶ Phase 1 — highest-risk (re-check first)
✅ digital_counter (was seven_segment) · ⚠ mandelbrot (REVOKED 2026-07-21) · ✅ julia · ⚠ burning_ship (REVOKED 2026-07-21) · ✅ heat_haze_map · ✅ thin_film ·
⚠ starfield (REVOKED 2026-07-21; moved → pattern_generators) · ✅ color_blindness (doc-only change, stays ✅) · ✅ false_color_exposure · ⚠ st_uv_map_inspector (REVOKED 2026-07-21; was stmap_qc_overlay) · ✅ uv_test_chart ·
✅ voronoi_edges · ✅ voronoi_manhattan · ✅ voronoi_chebyshev · ✅ hex_grid · ✅ smin_metaballs   ← Phase 1 done, then 4 revoked by the bug-fix pass
(these 16 were approved under the OLD format — re-confirmed under the new one 2026-07-07.)

### Phase 2 — remaining, heavier GLSL / node-deps
- stmap_generators: ✅ chromatic_aberration_map · ✅ coc_from_depth · ✅ glitch_block_map · ⚠ kaleidoscope_map (REVOKED 2026-07-21 — output-anchor fix) · ✅ lens_distort_map · ✅ polar_to_cartesian · ✅ thin_lens_coc   ← 7 Phase-2 items + heat_haze_map (Phase 1) = folder 8; 7/8 ✅
- stylization: ✅ bayer_dither (levels default 2→5) · ⚠ crosshatch (REVOKED 2026-07-21) · ✅ crt (added `scale` var for phosphor size, default 3) · ⚠ halftone (REVOKED 2026-07-21) · ⚠ palette_quantize (REVOKED 2026-07-21) · ✅ truchet (moved → pattern_generators)   ← 3 of 6 revoked by the bug-fix pass
- optics_physics: ✅ moire · ✅ radar_sweep · ✅ wave_interference (moved → pattern_generators)   ← optics_physics DONE (folder now holds moire + radar_sweep + thin_film, all ✅)
- control_surfaces: ✅ channel_pack (added md explanation of luma/3-matte packing) · ✅ channel_unpack · ⚠ dual_output_depth (REVOKED 2026-07-21 — strength default) · ⚠ painted_grade (REVOKED 2026-07-21 — hue-matrix fix)   ← 2 of 4 revoked
- sdf_shapes: ✅ sdf_lattice   ← see folder note above (2 revoked)
- pattern_generators: ✅ wood_grain · ✅ marble · ✅ triangle_tiling · ✅ log_polar_spiral · ✅ point_grid · ✅ zone_plate   ← see folder note above (2 revoked)
- diagnostics: ✅ clip_highlighter · ✅ contour_lines · ✅ exposure_zebra · ✅ gamut_clip · ✅ negative_pixel_highlighter · ⚠ zone_system_posterize (REVOKED 2026-07-21 — top-band clamp)   ← 8/9 ✅ (incl. the Phase-1 ones; st_uv_map_inspector also revoked, see Phase 1)

### Phase 3 — remaining, lighter per-pixel math
- color_grade: ✅ ALL 20 confirmed (cosine_palette, lens_vignette, log-curve pairs, saturation_by_luma, highlight_desaturate, hue_preserving_clip + Phase-4 basics)
- matte_combine: ✅ ALL 11 confirmed (holdout_matte, matte_screen_multiply, matte_falloff_ramp + set-op basics; matte_grade gained a `lift` var)
- alpha_matte_tools: 5/6 ✅ (alpha_crunch revoked 2026-07-21, see above)
- animated_generators: ✅ ALL 9 confirmed (waves + pulse_rings, spin_rays)
- aov_tools: motion_vector_visualize, motion_vector_normalize
- 3d_position_tools: normal_renormalize, normal_to_facing, position_range_remap

### Phase 4 — the rest (the old "83", lowest risk), by category
Everything not listed above. Re-confirm under the new format.

## How to present each setup (the per-item ritual)
For each: read `setups/<cat>/<name>.md`, then tell the user (1) which setup + one-line what,
(2) exact inputs to wire in Batch (Front 1/2, Matte 1/2, or "none — generator"; flag colour-space
and any required downstream node), (3) what to look for, (4) the real pass/fail. After the verdict,
tick the checklist above (✅/❌) — do NOT move the file.

## Recategorization candidates (apply via CATEGORY in generate_setups.py, then regenerate)
- **starfield**: optics_physics → pattern_generators — ✅ APPLIED 2026-07-07 (hash/noise-driven
  texture, not analytic physics). README row moved.
- **truchet**: stylization → pattern_generators — ✅ APPLIED 2026-07-07 (pure procedural tiling
  generator). README row moved.
- **wave_interference**: optics_physics → pattern_generators — ✅ APPLIED 2026-07-07 (procedural
  two-colour generator). README row moved.

## New backlog idea captured during eval (already in setup_expansion_backlog.md)
- `digital_counter` (7-seg) **alphabet/alphanumeric** — needs 14/16-segment layout; bigger truth
  table than the digit (already longest expression) → real expression-length risk. Compile-check early.
