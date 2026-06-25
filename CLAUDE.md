# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is
A library of **Autodesk Flame "Pixel Expression" node setups** (`.pixel_expression_node`
files) that translate the best Foundry Nuke expression-node examples into Flame's GLSL.
The Pixel Expression node (Flame 2027.1+) applies per-pixel GLSL to a clip's channels.

## Commands
Generator + validator are pure-stdlib Python 3 — no deps, no venv, no install step.
- `python3 tools/generate_setups.py` — regenerate all 155 `.pixel_expression_node` files +
  companion `.md` docs from the generator. Run after any edit to `tools/generate_setups.py`.
- `python3 tools/validate_setups.py` — static-check every generated setup. Must be **0
  errors** (errors on reserved-name collisions; warns on unused/undefined identifiers,
  unbalanced parens, bad slot counts). Run after every regenerate.
- `python3 tools/glsl_compile_check.py` — **optional pre-Flame gate**: compiles each setup's
  GLSL with `glslangValidator` (needs `brew install glslang`) to catch real compile errors the
  static checker can't. Calibrated against the Flame-verified setups (they all pass), so a clean
  run is strong evidence a new setup will compile in Flame — but it's a proxy, not a substitute
  for a real in-Flame load (can't prove Flame's exact dialect/length limits or visual output).
- `/sync-docs` — project command: does regenerate + validate + drift-check and syncs the
  counts and Live-Flame status across CLAUDE.md and README. Prefer this for routine edits.

There is no unit-test suite or build beyond the above — `validate_setups.py` (static) and
`glsl_compile_check.py` (compile) are the tests.

## ⚠️ ACTIVE: Live-Flame evaluation in progress — do NOT regenerate
A setup-by-setup **in-Flame load/visual test** is underway (started 2026-06-25). As each setup
passes/fails in Flame it is moved (`git mv`) into an **`approved/`** or **`rejected/`** subfolder
**inside its category folder**. Full tracker + resume point: `documentation/live_flame_eval_progress.md`.
- **Status:** 16/155 approved, 0 rejected. Phase 1 (the 16 highest-risk setups) is complete; next
  up is Phase 2, resuming at `stmap_generators/chromatic_aberration_map`.
- **DO NOT run `tools/generate_setups.py` or `/sync-docs` until the eval is finished.** The
  generator writes to `setups/<category>/<name>...` and doesn't clean first, so regenerating
  **resurrects the originals** beside the moved copies → duplicates. The validator and
  compile-checker use a recursive glob and are still safe to run. The planned final step is to
  teach the generator to emit into `approved/`/`rejected/` from an approval table, restoring the
  source-of-truth invariant — only then is regeneration safe again.

## Golden rule: never hand-edit the setup files
`tools/generate_setups.py` is the **single source of truth**. All 155 `.pixel_expression_node`
files and their companion `.md` docs are generated from it.
- Add/change a setup → edit the `SETUPS` list, then add its `CATEGORY`, `DOCS`, and
  `EXPECTS` entries (the script warns if `DOCS`/`EXPECTS` are missing). Optionally add a
  `NOTES` entry — long-form Markdown appended to the setup's `.md` under a `## Notes`
  heading (workflow, recipes, gotchas); all 155 setups currently have one.
- Regenerate: `python3 tools/generate_setups.py`
- Validate: `python3 tools/validate_setups.py` (must be **0 errors**; errors on reserved-name
  collisions — any var/formula shadowing a built-in/input; warns on unused vars / undefined
  identifiers / unbalanced parens / bad slot counts).
- Or just run `/sync-docs` — the project command that does regenerate + validate + drift
  check and syncs the counts and Live-Flame status across CLAUDE.md and README.
- The `.pixel_expression_node` files are XML; editing them by hand will drift from the
  generator and is almost never right.

## Key files
- `tools/generate_setups.py` — generator (SETUPS + CATEGORY + DOCS + EXPECTS + NOTES tables).
- `tools/validate_setups.py` — static checker.
- `tools/glsl_compile_check.py` — optional offline GLSL compile-check (`glslangValidator`); a
  pre-Flame gate for real compile errors. Not stdlib-only — needs `brew install glslang`.
- `.claude/commands/sync-docs.md` — the `/sync-docs` project command (regenerate, validate,
  drift-check, and sync counts + Live-Flame status across the hand-maintained docs).
- `README.md` — human index (per-folder tables, colour-management, caveats).
- `setups/` — the 155 generated `.pixel_expression_node` files + companion `.md` docs, in 19
  category subfolders (the loadable library).
- `documentation/pixelexpression1.pixel_expression_node` — a real Flame-saved file kept as a
  worked example of the serialization (the one the format doc was reverse-engineered from; do
  NOT delete). Its `.p` proxy thumbnail is gitignored — Flame regenerates it on load.
- `documentation/flame_pixel_expression_file_format.md` — reverse-engineered file format.
- `documentation/flame_pixel_expression_translations.md` — Nuke→Flame GLSL mapping.
- `documentation/node_dependencies.md` — every setup that needs an upstream pass or a
  downstream node (ST-map→STMap, CoC→Defocus, depth/P/normal/AOV/crypto consumers, paired
  pack/unpack, colour-management adjacency) with exact Batch wiring. Hand-maintained.
- `documentation/setup_expansion_backlog.md` — the tiered expansion backlog (idea list with
  formulas/inputs/gaps, ☐/☑ status). Tiers 1–4 are all built (the 2026-06-25 expansion); the
  only open items are the **Deferred / flagged** section (Apollonian fractal, single-pass
  domain-warp, CA-fringe overlay — each constraint-risky or redundant). Add new ideas here.
- `documentation/nuke_expressions_cheatsheet.md` — source Nuke reference.
- `documentation/flame_feature_showcase_setup.md` — recipe for a hand-built setup that
  exercises every node feature (front blend, vignette, sat/gamma, ring×ray matte).
- `documentation/PixelExpression.txt` — Foundry/Autodesk node docs (node intro).

## File format facts (the non-obvious ones)
- Single-line XML: `<Setup><Base>…</Base><State>…</State></Setup>`.
- Channel expressions: `<RedExpression>` `<GreenExpression>` `<BlueExpression>`
  `<MatteExpression>`. 8 variable slots, 4 formula slots — always emitted (unused = empty).
- `FormulaType`: `0`=float `1`=vec2 `2`=vec3 `3`=vec4.
- **Expressions must be XML-escaped**: `<`→`&lt;`, `>`→`&gt;`, `&`→`&amp;`. A raw `<`
  makes the file **silently fail to load with no error**. The generator handles this.
- Static value = un-keyed channel (`Size 0`, empty `<KFrames>`). Animation = a list of
  `(frame, value)` pairs → multi-key channel. Centre defaults to `0,0`, un-keyed.
- Input wiring is NOT stored — connect Front/Matte in Batch.

## GLSL / node gotchas
- It's GLSL, not Nuke syntax: float literals need a decimal (`1.0`, `x/2.0`); `clamp`
  needs min+max; `fmod`→`mod`; `hypot`→`length`; `atan(y,x)` order.
- **`uv` is a reserved injected variable** (normalized coords) — never name a
  variable/formula `uv` (redefinition error). Avoid `color`, `pos`, `coord`, `gl_*`.
- Inputs: `r1 g1 b1` (Front 1), `r2 g2 b2` (Front 2), `m1`/`m2` (Matte 1/2). Built-ins:
  `x y width height centre.x centre.y E PI`. No `frame`/time — animate a variable instead.
- **Confirmed:** the Matte expression CAN read Front inputs (`r1`…), and formulas can use
  Front inputs. But **OutMatte only renders when Matte 1 is connected**, whatever the
  expression references.
- No neighbour sampling (only the current pixel of each input).

## Conventions used across the library
- **Depth tools:** depth always arrives on **Matte 1 (`m1`)**.
- **Matte-generating setups** write the result to RGB *and* the Matte field (use Result or
  OutMatte).
- **Colour space:** the node does no colour management. Each setup's `.md` has an
  **Expects:** line (scene-linear / raw-data / any / conversion). Light math = linear;
  P/normal/depth/crypto = raw; ST-map output = data. See README "Colour management".
- **Two-colour patterns:** every tonal generator in `pattern_generators/` and
  `animated_generators/` (all except `noise_random`) blends `mix(A, B, pattern)` per
  channel via the `_two_color()` helper + shared `_COLVARS` (`aR/aG/aB`→`bR/bG/bB`,
  default black→white so the look is unchanged). Matte keeps the raw 0..1 pattern.
- **SDF shapes:** `_HOLLOW(extent)` adds a `hollow` 0..1 cut-out (0=solid). Exception:
  `sdf_rounded_box` subtracts a SECOND rounded box (formulas `wall`,`d`,`d2`, same
  `corner`) so the hole's corners match the exterior — an inward SDF offset would sharpen
  them.
- **Noise:** every `noise/` generator has a `seed` (offset into the field — keyframe it to
  drift/evolve) plus shaping vars (`gain`, `lacunarity`/`persistence`, `jitter`).
- **Node dependencies:** some setups are only one stage of a Batch graph — ST-map generators
  (`uv_distortion/`, `stmap_generators/`, `utility/stmap`) emit a UV map for a downstream
  **STMap**; `coc_from_depth`/`depth_dof_mask` feed a **variable-blur/Defocus**; depth / P /
  normal / AOV / crypto tools need a specific pass wired **upstream**; `channel_pack`↔
  `channel_unpack` and `rgb_to_hsv`↔`hsv_to_rgb` are pairs. These are recorded in the `DEPENDS`
  table (renders a **## Node dependencies** section into each `.md`) and explained in full in
  `documentation/node_dependencies.md` — keep the two in sync when adding a node-dependent setup.

## Reuse the generator helpers
Before writing new GLSL, check the helpers near the top of `tools/generate_setups.py`:
`DIST`/`DIST3` (distance formulas), `_two_color()`/`_COLVARS`, `_solid()` (write one expr to
RGB+Matte for a matte generator), `_HOLLOW()`, the noise builders (`_VALUE_NOISE`,
`_FBM_NOISE`, `_VORONOI`, `_vnoise_at`, `_hash2`), and the HSV/colour helpers (`HSV_P`,
`HSV_Q`, `_HUE`, `_SAT`, `_LUMA`, the `_HROT_R/G/B` hue-rotation matrix rows, `_hue_band()`,
`_hue2rgb()`). Variable budget is 8; colour vars eat 6. HSV decode (`HSV_P`+`HSV_Q`) eats 2
of the 4 formula slots.

The later experimental categories add their own helper families (also near the top of the
generator): `_fractal_chain()`/`_fractal_step()` + `_FRAC_ESCAPE`/`_FRAC_PIX` (the 4-formula
escape-time chain — see the fractal architecture note under "Live-Flame status"); the
seven-segment builders `_seven_seg_expr()`/`_seg_bar()`/`_seg_eq()` + `_SEG_ON`/`_SEG_GEO` and
`_LUMA01`; and the `DEPENDS`/`_dep()` machinery that renders each setup's node-dependency
section. `stylization/` setups are collected in a `_STYLIZATION` list appended to `SETUPS`.

## Folders (155 setups, all under `setups/`)
`alpha_matte_tools` `pattern_generators` `animated_generators` `color_grade`
`3d_position_tools` `depth_tools` `aov_tools` `uv_distortion` `noise` `sdf_shapes`
`hsv_color` `matte_combine` `utility`

**Unconventional / experimental categories (added later, see "Live-Flame status"):**
`fractals` `stmap_generators` `control_surfaces` `stylization` `optics_physics` `diagnostics`
- `fractals` — escape-time Mandelbrot/Julia/Burning-Ship. **Architecture-limited to 8
  iterations** (the node has no reassignable state; the only way to iterate is the 4-formula
  chain, and inlining a complex square expands the string ~8× per step, so K=2/formula is the
  ceiling). Interiors read solid, edges band — a texture tool, not a deep-zoom renderer.
- `stmap_generators` — these OUTPUT a map (UV coords or a scalar) to be consumed by a
  **downstream node**; there is no neighbour sampling, so the gather happens elsewhere. Each
  `.md` "Notes" states the required downstream node (STMap for the UV maps; a variable-blur /
  Defocus for `coc_from_depth`).
- `control_surfaces` — Front 2 / Matte 2 used as a painted control surface (spatially-varying
  parameters) and the node's two-outputs-at-once trick (`dual_output_depth`).
- `stylization` `optics_physics` `diagnostics` — per-pixel looks, analytic physics generators,
  and in-comp inspection tools (colour-blindness sim, exposure zebra, gamut clip).

Note: procedural noise (`noise/`) and HSV/voronoi expressions are large and built
programmatically in `tools/generate_setups.py` (the node has no user-defined GLSL functions,
so everything is inlined). All are verified in Flame, but they're the most complex GLSL in
the library — so if you edit one, they're the most likely to need a fresh live-compile check.

## Live-Flame status
- **The original 83 setups are verified loading and working in Flame** (every folder up to and
  including `utility`, incl. the branchless rgb↔hsv conversions, the full
  `aov_tools/`/`depth_tools/`/`3d_position_tools/`/`uv_distortion/` sets, and `hsl_targeted` —
  the longest single expression in the library).
- **The remaining 72 setups pass an offline GLSL compile-check but are NOT yet confirmed loading
  in Flame.** These are the 29 in the six unconventional categories (`fractals`,
  `stmap_generators`, `control_surfaces`, `stylization`, `optics_physics`, `diagnostics`), **plus
  the 43 added in the 2026-06-25 expansion (Tiers 1–4)**: Tier-1 (`cosine_palette`,
  `lens_vignette`, `false_color_exposure`, `contour_lines`, `stmap_qc_overlay`, `uv_test_chart`,
  `point_grid`, `zone_plate`, `thin_lens_coc`); Tier-2 log curves
  `cineon_to_linear`/`linear_to_cineon`/`logc_to_linear`/`linear_to_logc`/`acescct_to_linear`/
  `linear_to_acescct` + `saturation_by_luma`, `highlight_desaturate`, `hue_preserving_clip`,
  `garbage_gradient_matte`, `holdout_matte`, `matte_screen_multiply`, `matte_falloff_ramp`,
  `negative_pixel_highlighter`, `clip_highlighter`, `zone_system_posterize`; Tier-3 AOV tools
  `motion_vector_visualize`, `motion_vector_normalize`, `normal_renormalize`, `normal_to_facing`,
  `position_range_remap`; Tier-4 patterns `voronoi_edges`, `voronoi_manhattan`,
  `voronoi_chebyshev`, `hex_grid`, `sdf_lattice`, `smin_metaballs`, `wood_grain`, `marble`,
  `triangle_tiling`, `log_polar_spiral`, `wave_bounce`, `wave_blip`, `wave_parabolic`. All 155
  setups compile cleanly under `tools/glsl_compile_check.py` (`glslangValidator`,
  `#version 410 core`) — and because the 83 already-Flame-verified setups all pass that same check,
  it's a well-calibrated proxy: a clean compile is strong evidence they will load. What it can't
  confirm: Flame's exact dialect/expression-length acceptance, OutMatte wiring, and visual
  correctness. So treat them as **compile-checked, in-Flame confirmation pending** — do a real load
  before fully trusting. (Some are additionally **math-verified**: the Tier-2 log curves round-trip
  against published anchors — LogC 0.18→0.391, ACEScct 0.18→0.4136 — and the `voronoi_edges` F1/F2
  trick and `smin_metaballs` smooth-min were numerically checked.) Highest-risk to check first:
  `seven_segment` (its `seg` formula is the longest single expression in the library now),
  the three `fractals` (deeply-nested vec3 formula chains), `heat_haze_map` (inlines the fbm
  builder), `thin_film`/`starfield` (swizzled vec formulas), `color_blindness` (4 matrix
  formulas), `false_color_exposure` / `stmap_qc_overlay` / `uv_test_chart` (nested vec3 `mix`
  cascades, and the first setups to read the injected `uv`), and from the Tier-4 wave
  `voronoi_edges` / `voronoi_manhattan` / `voronoi_chebyshev` (9-term distance chains — the
  heaviest new GLSL, `voronoi_edges` writes its F1/F2 distance set twice), `hex_grid` (the `gv`
  nearest-centre ternary), and `smin_metaballs` (nested smooth-min). If any fails to load, fix it
  in `tools/generate_setups.py` and regenerate.
- **History/lesson:** `hsl_targeted` first failed to load because it declared a variable
  `width` (collides with the injected built-in `width`); renamed to `bandWidth`. The
  validator now flags ANY var/formula that shadows a built-in/input (not just `uv`), so this
  whole silent-no-load class is caught statically — re-run `tools/validate_setups.py` after edits.
- If the user reports a load/compile failure, fix the expression in `tools/generate_setups.py`
  and regenerate — never patch the `.pixel_expression_node` directly. A silent
  no-error load failure usually means an unescaped `<`/`>` or a reserved name — a built-in
  (`uv`, `x`, `y`, `width`, `height`, `centre`, `E`, `PI`) or input (`r1`…) used as a
  variable/formula; `tools/validate_setups.py` now catches the reserved-name case.
- **Outstanding next step (to continue later):** the **in-Flame load test is actively in progress**
  (see the "ACTIVE" section at the top + `documentation/live_flame_eval_progress.md`). **16 of the 72
  compile-checked-pending setups are now Flame-verified** (all of Phase 1, the highest-risk batch) and
  live in `approved/` subfolders; **56 pending remain**, plus a Phase-4 re-confirm pass over the
  original 83. **Resume at `stmap_generators/chromatic_aberration_map`** (Phase 2). Counts here/README
  are NOT yet reconciled via `/sync-docs` — that's deferred until the eval finishes and the generator
  learns the `approved/`/`rejected/` layout (running `/sync-docs` now would regenerate and duplicate).
  For *more* setups, pull the next idea from `documentation/setup_expansion_backlog.md` — Tiers 1–4 are
  done; only the Deferred / flagged items remain (constraint-risky), so net-new ideas go there first.
