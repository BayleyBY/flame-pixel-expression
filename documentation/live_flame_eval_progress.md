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

## Status: 22 / 156 confirmed (new format)  ·  ✅ PHASE 1 COMPLETE (all 16 highest-risk)
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
- stmap_generators: chromatic_aberration_map, coc_from_depth, glitch_block_map, kaleidoscope_map, lens_distort_map, polar_to_cartesian, thin_lens_coc
- stylization: bayer_dither, crosshatch, crt, halftone, palette_quantize, truchet
- optics_physics: moire, radar_sweep, wave_interference
- control_surfaces: channel_pack, channel_unpack, dual_output_depth, painted_grade
- sdf_shapes: sdf_lattice
- pattern_generators: wood_grain, marble, triangle_tiling, log_polar_spiral, point_grid, zone_plate
- diagnostics: clip_highlighter, contour_lines, exposure_zebra, gamut_clip, negative_pixel_highlighter, zone_system_posterize

### Phase 3 — remaining, lighter per-pixel math
- color_grade: cosine_palette, lens_vignette, cineon_to_linear, linear_to_cineon, logc_to_linear, linear_to_logc, acescct_to_linear, linear_to_acescct, saturation_by_luma, highlight_desaturate, hue_preserving_clip
- matte_combine: holdout_matte, matte_screen_multiply, matte_falloff_ramp
- alpha_matte_tools: garbage_gradient_matte
- animated_generators: wave_bounce, wave_blip, wave_parabolic
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
  texture, not analytic physics). README per-folder tables still need the row moved (defer to a
  sync pass).

## New backlog idea captured during eval (already in setup_expansion_backlog.md)
- `digital_counter` (7-seg) **alphabet/alphanumeric** — needs 14/16-segment layout; bigger truth
  table than the digit (already longest expression) → real expression-length risk. Compile-check early.
