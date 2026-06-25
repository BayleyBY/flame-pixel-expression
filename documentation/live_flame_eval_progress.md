# Live-Flame evaluation — progress tracker

Working through an **in-Flame load/visual test of every setup**, one at a time. The user loads
each in Flame, approves or rejects, and the setup + its `.md` are moved into an `approved/` or
`rejected/` subfolder **inside its category folder**. Started 2026-06-25.

## ⚠️ CRITICAL — do NOT regenerate while this is in progress
`tools/generate_setups.py` writes each setup to `setups/<category>/<name>...` and does **not**
clean the folder first. Running the generator (or `/sync-docs`, which regenerates) will
**resurrect the originals** next to the moved `approved/`/`rejected/` copies → duplicates.
- The **validator** and **compile-checker** use a recursive glob, so they still work after moves.
- Only **regeneration** is unsafe. So: **don't run `generate_setups.py` or `/sync-docs`** until
  the eval is finished and the generator has been taught to emit into `approved/`/`rejected/`
  subfolders (a `STATUS`/approval table → category path). That generator change is the planned
  final step that restores the source-of-truth invariant.

## Progress = filesystem
- Setup still directly in `setups/<category>/` → **not yet evaluated**.
- In `setups/<category>/approved/` → **approved (Flame-verified)**.
- In `setups/<category>/rejected/` → **rejected** (fix in generator later).
Quick count:
```
find setups -path '*/approved/*.pixel_expression_node' | wc -l
find setups -path '*/rejected/*.pixel_expression_node' | wc -l
```

## Scope / order (decided with user)
- **Scope:** all 155 (including the 83 already-Flame-verified — re-confirm them too).
- **Order:** highest-risk first (CLAUDE.md risk list), then remaining pending, then the 83.

## Status: 16 / 155 approved, 0 rejected

### ✅ Phase 1 — documented highest-risk (16/16 DONE, all approved)
seven_segment · mandelbrot · julia · burning_ship · heat_haze_map · thin_film · starfield ·
color_blindness · false_color_exposure · stmap_qc_overlay · uv_test_chart · voronoi_edges ·
voronoi_manhattan · voronoi_chebyshev · hex_grid · smin_metaballs

### ▶ Phase 2 — remaining pending, heavier GLSL / node-deps (NEXT)
**Resume here →** `stmap_generators/chromatic_aberration_map` was *presented and is awaiting the
user's verdict* — re-present it first tomorrow.
- stmap_generators: chromatic_aberration_map (awaiting verdict), coc_from_depth, glitch_block_map, kaleidoscope_map, lens_distort_map, polar_to_cartesian, thin_lens_coc
- stylization: bayer_dither, crosshatch, crt, halftone, palette_quantize, truchet
- optics_physics: moire, radar_sweep, wave_interference
- control_surfaces: channel_pack, channel_unpack, dual_output_depth, painted_grade
- sdf_shapes: sdf_lattice
- pattern_generators: wood_grain, marble, triangle_tiling, log_polar_spiral, point_grid, zone_plate
- diagnostics: clip_highlighter, contour_lines, exposure_zebra, gamut_clip, negative_pixel_highlighter, zone_system_posterize

### Phase 3 — remaining pending, lighter per-pixel math
- color_grade: cosine_palette, lens_vignette, cineon_to_linear, linear_to_cineon, logc_to_linear, linear_to_logc, acescct_to_linear, linear_to_acescct, saturation_by_luma, highlight_desaturate, hue_preserving_clip
- matte_combine: holdout_matte, matte_screen_multiply, matte_falloff_ramp
- alpha_matte_tools: garbage_gradient_matte
- animated_generators: wave_bounce, wave_blip, wave_parabolic
- aov_tools: motion_vector_visualize, motion_vector_normalize
- 3d_position_tools: normal_renormalize, normal_to_facing, position_range_remap

### Phase 4 — the 83 already Flame-verified (lowest risk), by category
Everything not listed above. Re-confirm and move into `approved/`.

## How to present each setup (the per-item ritual)
For each: read `setups/<cat>/<name>.md`, then tell the user (1) which setup + one-line what,
(2) exact inputs to wire in Batch (Front 1/2, Matte 1/2, or "none — generator"; flag colour-space
and any required downstream node), (3) what to look for, (4) the real pass/fail. After verdict:
`git mv` (fallback `mv`) both files into `approved/` or `rejected/`, then present the next.

## Recategorization candidates (apply via CATEGORY in generate_setups.py at the FINAL step, not manual move)
- **starfield**: optics_physics → pattern_generators (hash/noise-driven texture, not analytic physics). User raised + approved 2026-06-25.

## New backlog idea captured during eval (already in setup_expansion_backlog.md)
- seven_segment **alphabet/alphanumeric** — needs 14/16-segment layout; bigger truth table than the
  digit (already longest expression) → real expression-length risk. Compile-check early.
