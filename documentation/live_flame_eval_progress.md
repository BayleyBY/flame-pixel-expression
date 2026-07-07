# Live-Flame evaluation — progress tracker

Working through an **in-Flame load/visual test of every setup**, one at a time. The user loads
each in Flame and approves or rejects it.

## ⚠️ RESET after the PR245 node format change (2026-07-07)
A Pixel Expression node update **changed the save-file XML** (variables → `<Variables>` list, new
`<…Declarations>` blocks, lean static channels — see `flame_pixel_expression_file_format.md`). Old
-format files no longer load, so **all prior approvals are void** and the eval restarts from **0/155**
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
- **Scope:** all 155 setups (new format — none carry over from the old eval).
- **Order:** highest-risk first (heaviest GLSL, below), then the rest by category.

## Status: 111 / 156 confirmed (new format)  ·  ✅ PHASE 1 & PHASE 2 COMPLETE · ▶ Phase 3/4 (basics) underway

### ▶▶ RESUME HERE (next session) — 45 setups left, all lower-risk basics
Confirm the remaining folders (whole-folder batches have been passing fast; the file wrapper is the
only thing that changed, GLSL is unchanged). **Remaining folders:**
- `aov_tools/` (motion_vector_visualize/normalize + albedo_divide/multiply, ao_multiply, aov_add,
  aov_clamp_negative, aov_grade_add, crypto_pick_2rank/4rank, id_isolate, screen_merge)
- `3d_position_tools/` (normal_renormalize, normal_to_facing, position_range_remap + pmatte_sphere/
  rings/rays, box_matte, normal_relight, fresnel_facing)
- `depth_tools/` (depth_normalize, depth_matte, depth_dof_mask, depth_contours, depth_posterize,
  depth_fog, depth_fade)
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
- ✅ **`alpha_matte_tools/` (6)** confirmed 2026-07-07 (alpha_crunch, fill_alpha, alpha_fringe,
  luma_key, difference_matte, garbage_gradient_matte).
- ✅ **`animated_generators/` (9)** confirmed 2026-07-07 (wave_sine/triangle/square/sawtooth/bounce/
  blip/parabolic + pulse_rings, spin_rays — animated `t` motion confirmed).
- ✅ **entire `sdf_shapes/` folder (8)** confirmed 2026-07-07: sdf_lattice (Phase 2), smin_metaballs
  + metaball_ring (already ✅), + sdf_box/sdf_circle/sdf_polygon/sdf_ring/sdf_rounded_box (Phase 4).
- ✅ **entire `pattern_generators/` folder (16)** confirmed 2026-07-07: wood_grain, marble,
  triangle_tiling, log_polar_spiral, point_grid, zone_plate (Phase 2) + bricks, checkerboard,
  noise_random, rays, rings (Phase 4) + already-✅ radial_ramp, hex_grid, starfield, truchet,
  wave_interference.

### ⚠️ Centre-convention fix (2026-07-07) — 4 stmap setups re-opened
PR245 defaults Centre to the image middle. Four ST-map setups did their OWN `-0.5` centering and
treated `centre` as an *offset from middle* (`(x+0.5)/width - 0.5 - centre.x/width`), so the new
middle default double-shifted their pole/optical-centre into the corner. Fixed to use `centre` as
an **absolute pole** (like `radial_ramp`): `((x + 0.5 - centre.x) / width)`, and dropped the now-
wrong `0.5 +` origin in the lens/chromatic output. Affected: `polar_to_cartesian`, `kaleidoscope_map`,
`lens_distort_map`, `chromatic_aberration_map` — the last 3 were "passed" mis-centered (not obvious
as abstract maps), so their passes are **revoked pending re-check**. Lesson: any setup that
normalizes coords itself and subtracts a normalized `centre` needs this treatment.
Library is now **156** (added `metaball_ring`). Animated channel (thin_film `shift`, metaball_ring
`spin`) confirmed live.
- ✅ **entire `noise/` folder (7)** confirmed 2026-07-07: voronoi_edges, voronoi_manhattan,
  voronoi_chebyshev (Phase 1) + voronoi, noise_value, noise_fbm, noise_cells (Phase 4).

### New setups added during the eval (net-new, not from the old 155)
- ✅ `sdf_shapes/metaball_ring` — 6 blobs on a ring (smooth-min welded), `spin` rotates. Built +
  confirmed 2026-07-07 as the higher-count companion to `smin_metaballs` (which caps at 3 for the
  8-var budget). File 4.4 KB, well within the expression-length limit.
- ✅ `pattern_generators/radial_ramp` — confirmed during the PR245 fix (loads, 8 vars + `dist`
  formula present, glow centred at image middle, radius pixel-accurate).
- ✅ `stylization/digital_counter` — 2026-07-07; loads + renders a clean digit at Centre (the
  library's longest expression). **Renamed from `seven_segment`** at the user's request.

### ▶ Phase 1 — highest-risk (re-check first)
✅ digital_counter (was seven_segment) · ✅ mandelbrot · ✅ julia · ✅ burning_ship · ✅ heat_haze_map · ✅ thin_film ·
✅ starfield (moved → pattern_generators) · ✅ color_blindness · ✅ false_color_exposure · ✅ st_uv_map_inspector (was stmap_qc_overlay) · ✅ uv_test_chart ·
✅ voronoi_edges · ✅ voronoi_manhattan · ✅ voronoi_chebyshev · ✅ hex_grid · ✅ smin_metaballs   ← Phase 1 done ✅
(these 16 were approved under the OLD format — re-confirm under the new one; expected to pass fast.)

### Phase 2 — remaining, heavier GLSL / node-deps
- stmap_generators: ✅ chromatic_aberration_map · ✅ coc_from_depth · ✅ glitch_block_map · ✅ kaleidoscope_map · ✅ lens_distort_map · ✅ polar_to_cartesian · ✅ thin_lens_coc   ← stmap_generators DONE (7/7)
- stylization: ✅ bayer_dither (levels default 2→5) · ✅ crosshatch · ✅ crt (added `scale` var for phosphor size, default 3) · ✅ halftone · ✅ palette_quantize · ✅ truchet (moved → pattern_generators)   ← stylization DONE (6/6)
- optics_physics: ✅ moire · ✅ radar_sweep · ✅ wave_interference (moved → pattern_generators)   ← optics_physics DONE (only moire + radar_sweep remain in the folder)
- control_surfaces: ✅ channel_pack (added md explanation of luma/3-matte packing) · ✅ channel_unpack · ✅ dual_output_depth · ✅ painted_grade   ← control_surfaces DONE (4/4)
- sdf_shapes: ✅ sdf_lattice   ← whole sdf_shapes folder confirmed (see note above)
- pattern_generators: ✅ wood_grain · ✅ marble · ✅ triangle_tiling · ✅ log_polar_spiral · ✅ point_grid · ✅ zone_plate   ← whole pattern_generators folder confirmed (16/16)
- diagnostics: ✅ clip_highlighter · ✅ contour_lines · ✅ exposure_zebra · ✅ gamut_clip · ✅ negative_pixel_highlighter · ✅ zone_system_posterize   ← diagnostics DONE (9/9, incl. the 3 Phase-1 ones)

### Phase 3 — remaining, lighter per-pixel math
- color_grade: ✅ ALL 20 confirmed (cosine_palette, lens_vignette, log-curve pairs, saturation_by_luma, highlight_desaturate, hue_preserving_clip + Phase-4 basics)
- matte_combine: ✅ ALL 11 confirmed (holdout_matte, matte_screen_multiply, matte_falloff_ramp + set-op basics; matte_grade gained a `lift` var)
- alpha_matte_tools: ✅ ALL 6 confirmed
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
