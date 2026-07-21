# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is
A library of **Autodesk Flame "Pixel Expression" node setups** (`.pixel_expression_node`
files) that translate the best Foundry Nuke expression-node examples into Flame's GLSL.
The Pixel Expression node (Flame 2027.1+) applies per-pixel GLSL to a clip's channels.

This repo is **local-only by design** — git has no remote. Never add one, push, or publish it.

## Commands
Generator + validator are pure-stdlib Python 3 — no deps, no venv, no install step.
- `python3 tools/generate_setups.py` — regenerate all 156 `.pixel_expression_node` files +
  companion `.md` docs from the generator. Run after any edit to `tools/generate_setups.py`.
- `python3 tools/validate_setups.py` — static-check every generated setup. Must be **0
  errors** (ERRORS: reserved-name collisions, undefined identifiers, unbalanced/mis-nested
  parens, missing/invalid slots, empty expressions, >8 variables, duplicate names, GLSL
  keywords as names, forward formula references; warns on unused vars/formulas and
  GLSL-function-name shadowing). Exits non-zero on errors, so it gates in scripts. Run
  after every regenerate.
- `python3 tools/glsl_compile_check.py` — **optional pre-Flame gate**: compiles each setup's
  GLSL with `glslangValidator` (needs `brew install glslang`; `-v` prints per-file compiler
  output) to catch real compile errors the static checker can't. Calibrated against the Flame-verified setups (they all pass), so a clean
  run is strong evidence a new setup will compile in Flame — but it's a proxy, not a substitute
  for a real in-Flame load (can't prove Flame's exact dialect/length limits or visual output).
- `/sync-docs` — project command: does regenerate + validate + drift-check and syncs the
  counts and Live-Flame status across CLAUDE.md and README. Prefer this for routine edits.

There is no unit-test suite or build beyond the above — `validate_setups.py` (static) and
`glsl_compile_check.py` (compile) are the tests. All three tools run over the **whole library**
each time (no single-setup flag) — a full run takes seconds, so there's nothing to scope down.

## ⚠️ Node format changed (PR245, 2026-07-07) — library regenerated, eval reset
A Pixel Expression node update **changed the save-file XML structure**, so every old-format setup
silently failed to load. The format was re-reverse-engineered from fresh Flame saves (kept in
`PR245/`), the generator + both checker tools were updated, and **all 156 setups were regenerated
to the new format**. See "File format facts" and "Live-Flame status" below for the delta.
- **Regeneration is safe again.** The old `approved/`/`rejected/` subfolders were flattened (the
  16 old-format approvals no longer load in the updated node), so the layout is flat again and
  `tools/generate_setups.py` writes the single source of truth with no duplication risk.
- **The Live-Flame eval reset to 0/156** against the updated node on 2026-07-07 and is now well
  underway (~96/156, Phases 1 & 2 complete; a 2026-07-21 semantic bug-fix pass changed 17
  setups' GLSL and revoked 15 previous passes — see the tracker). Because only the *file
  wrapper* changed in PR245 (GLSL untouched), re-verification has been fast — whole folders
  pass in a batch. Tracker (source of truth for the live count):
  `documentation/live_flame_eval_progress.md`.

## Golden rule: never hand-edit the setup files
`tools/generate_setups.py` is the **single source of truth**. All 156 `.pixel_expression_node`
files and their companion `.md` docs are generated from it.
- Add/change a setup → edit the `SETUPS` list, then add its `CATEGORY`, `DOCS`, and
  `EXPECTS` entries (the script warns if `DOCS`/`EXPECTS` are missing). Optionally add a
  `NOTES` entry — long-form Markdown appended to the setup's `.md` under a `## Notes`
  heading (workflow, recipes, gotchas); all 156 setups currently have one.
- Regenerate: `python3 tools/generate_setups.py`
- Validate: `python3 tools/validate_setups.py` (must be **0 errors**; reserved-name
  collisions — any var/formula shadowing a built-in/input — plus undefined identifiers,
  paren problems and slot issues are all ERRORS; unused vars/formulas are warnings).
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
- `setups/` — the 156 generated `.pixel_expression_node` files + companion `.md` docs, in 19
  category subfolders (the loadable library).
- `documentation/pixelexpression1.pixel_expression_node` — a real Flame-saved file kept as a
  worked example of the **old pre-PR245** serialization (the original format doc was
  reverse-engineered from it; it no longer loads in the updated node — the current-format
  reference saves live in `PR245/`. Do NOT delete either). Its `.p` proxy thumbnail is
  gitignored — Flame regenerates it on load.
- `documentation/flame_pixel_expression_file_format.md` — reverse-engineered file format.
- `documentation/flame_pixel_expression_translations.md` — Nuke→Flame GLSL mapping.
- `documentation/node_dependencies.md` — every setup that needs an upstream pass or a
  downstream node (ST-map→STMap, CoC→Defocus, depth/P/normal/AOV/crypto consumers, paired
  pack/unpack, colour-management adjacency) with exact Batch wiring. Hand-maintained.
- `documentation/setup_expansion_backlog.md` — the tiered expansion backlog (idea list with
  formulas/inputs/gaps, ☐/☑ status). Tiers 1–4 are all built (the 2026-06-25 expansion); the
  only open items are the **Deferred / flagged** section (Apollonian fractal, single-pass
  domain-warp, CA-fringe overlay — each constraint-risky or redundant) plus the
  `digital_counter` alphanumeric idea captured during the eval. Add new ideas here.
- `documentation/nuke_expressions_cheatsheet.md` — source Nuke reference.
- `documentation/flame_feature_showcase_setup.md` — recipe for a hand-built setup that
  exercises every node feature (front blend, vignette, sat/gamma, ring×ray matte).
- `documentation/PixelExpression.txt` — Foundry/Autodesk node docs (node intro).

## File format facts (the non-obvious ones)
- Single-line XML: `<Setup><Base>…</Base><State>…</State></Setup>`.
- Channel expressions: `<RedExpression>` `<GreenExpression>` `<BlueExpression>`
  `<MatteExpression>`, each followed by a matching **`<…Declarations>`** block (new PR245
  format — holds the multi-line Expression Editor's local declarations; we emit them empty).
- **Variables (new PR245 format):** a single `<Variables>` container holding one
  `<Variable index="N" name="…"><Channel Name="scene/<node>/<name>">…</Channel></Variable>`
  per *defined* variable (not the old 8 fixed `Variable0..7`/`VariableName0..7` slots). The
  channel path uses the variable **name**, not `variableN`. The whole `<Variables>` block is
  **omitted** when a setup has no variables. Still capped at 8 by the UI. Reading the old flat
  slots is what broke both checker tools after the update.
- **Formulas are unchanged:** still 4 fixed slots `<FormulaName/Expression/Type 0..3>`, always
  emitted (unused = empty). `FormulaType`: `0`=float `1`=vec2 `2`=vec3 `3`=vec4.
- **Expressions must be XML-escaped**: `<`→`&lt;`, `>`→`&gt;`, `&`→`&amp;`. A raw `<`
  makes the file **silently fail to load with no error**. The generator handles this.
- **Channels:** a *static* channel is now the **lean** form
  `<Channel Name><Extrap>constant</Extrap><Value>V</Value><Uncollapsed/></Channel>` (no
  `<Size>`/`<KeyVersion>`/`<KFrames>`). An *animated* channel keeps the old
  `Size`/`KeyVersion`/`KFrames`/`Key` block (a list of `(frame, value)` pairs).
- **Centre now defaults to the image middle (PR245).** At runtime `centre.x`/`centre.y` inject as
  the **middle pixel coords** (≈`width/2`, `height/2`) by default — NOT `0`. `x`/`y` and pixel
  distances are unchanged. **Convention: use `centre` as an ABSOLUTE focal point** (`x - centre.x`,
  like `radial_ramp` and the SDF shapes) — those auto-centre and follow the Centre manipulator
  correctly. **Do NOT do your own `-0.5` centering and then subtract a normalized `centre`**
  (`(x+0.5)/width - 0.5 - centre.x/width`): that treats `centre` as an offset-from-middle and now
  double-shifts by the new default, pushing the pole to a corner. This bit the four ST-map
  generators (`polar_to_cartesian`/`kaleidoscope_map`/`lens_distort_map`/`chromatic_aberration_map`)
  — fixed to `((x + 0.5 - centre.x)/width)`. Both `centre` and `center` spellings are recognised.
- Input wiring is NOT stored — connect Front/Matte in Batch. OutMatte output is tagged as Matte.

## GLSL / node gotchas
- It's GLSL, not Nuke syntax: float literals need a decimal (`1.0`, `x/2.0`); `clamp`
  needs min+max; `fmod`→`mod`; `hypot`→`length`; `atan(y,x)` order.
- **`uv` is a reserved injected variable** (normalized coords) — never name a
  variable/formula `uv` (redefinition error). Avoid `color`, `pos`, `coord`, `gl_*`.
- Inputs: `r1 g1 b1` (Front 1), `r2 g2 b2` (Front 2), `m1`/`m2` (Matte 1/2). Built-ins:
  `x y width height centre.x centre.y E PI` (also `center.*` — both spellings recognised since
  PR245; `centre` now sits at the image middle). No `frame`/time — animate a variable instead.
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
  `animated_generators/` (all except `noise_random`, `starfield` and `log_polar_spiral`,
  whose variable budgets are spent on their own controls) blends `mix(A, B, pattern)` per
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
  **STMap**; `coc_from_depth`/`thin_lens_coc`/`depth_dof_mask` feed a **variable-blur/Defocus**; depth / P /
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

## Folders (156 setups, all under `setups/`)
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
  Defocus for `coc_from_depth`/`thin_lens_coc`).
- `control_surfaces` — Front 2 / Matte 2 used as a painted control surface (spatially-varying
  parameters) and the node's two-outputs-at-once trick (`dual_output_depth`).
- `stylization` `optics_physics` `diagnostics` — per-pixel looks, analytic physics generators,
  and in-comp inspection tools (colour-blindness sim, exposure zebra, gamut clip).

Note: procedural noise (`noise/`) and HSV/voronoi expressions are large and built
programmatically in `tools/generate_setups.py` (the node has no user-defined GLSL functions,
so everything is inlined). All are verified in Flame, but they're the most complex GLSL in
the library — so if you edit one, they're the most likely to need a fresh live-compile check.

## Live-Flame status
- **The PR245 format change reset the in-Flame verification.** All prior in-Flame approvals (the
  original 83 + the 16 Phase-1 approvals) were against the **old** file format/node and **do not
  transfer** — those old-format files no longer load. All 156 setups have been **regenerated to the
  new format** and now need a fresh in-Flame load pass. Good news: only the *file wrapper* changed
  (GLSL/expressions untouched), so most should re-verify quickly.
- **Confirmed in the updated node so far:** see `documentation/live_flame_eval_progress.md` for the
  live count (**Phases 1 & 2 are complete** — all 16 highest-risk plus the unconventional/experimental
  folders — and the lower-risk basics are being batch-confirmed folder-by-folder; ~96/156 confirmed:
  111 as of the last session minus 15 passes revoked by the 2026-07-21 bug-fix pass. Resume at
  `aov_tools/`, then re-verify the revoked list). The new format is proven correct, including animated
  channels (`thin_film`/`metaball_ring`). Everything not yet ticked is **new-format, in-Flame
  confirmation pending** — the tracker doc is the source of truth for the exact count.
- **All 156 pass the offline checkers** (both recalibrated for the new format):
  `tools/validate_setups.py` → 0 errors/0 warnings, and `tools/glsl_compile_check.py`
  (`glslangValidator`, `#version 410 core`) → 156 compile. A clean compile is strong evidence a
  setup will load, but can't confirm Flame's exact dialect/expression-length acceptance, OutMatte
  wiring, or visual correctness — do a real load before fully trusting.
- **Highest-risk to re-check first** (heaviest GLSL — most likely to expose a dialect/length limit):
  `digital_counter` (the 7-segment digit — longest single expression), the three `fractals` (deeply-nested vec3 formula
  chains), `heat_haze_map` (inlines the fbm builder), `thin_film`/`starfield` (swizzled vec
  formulas), `color_blindness` (4 matrix formulas), `false_color_exposure`/`st_uv_map_inspector`/
  `uv_test_chart` (nested vec3 `mix` cascades; read the injected `uv`), and the Voronoi trio
  `voronoi_edges`/`voronoi_manhattan`/`voronoi_chebyshev` (9-term distance chains), `hex_grid`
  (the `gv` nearest-centre ternary), `smin_metaballs` (nested smooth-min).
- **History/lessons (still apply):**
  - `hsl_targeted` first failed to load because it declared a variable `width` (collides with the
    injected built-in). The validator flags ANY var/formula shadowing a built-in/input — re-run it
    after edits.
  - The **PR245 break** was purely structural: the new node stores variables as a `<Variables>`
    name-keyed list + adds `<…Declarations>` blocks, and both checker tools were reading the old
    flat `Variable0..7` slots (they reported everything undefined until updated). If load/compile
    tooling suddenly reports mass-undefined identifiers after a node update, suspect a format change
    first — re-diff a fresh Flame save against `PR245/` using the method in `documentation/`.
- If the user reports a load/compile failure, fix the expression in `tools/generate_setups.py`
  and regenerate — never patch the `.pixel_expression_node` directly. A silent no-error load failure
  usually means an unescaped `<`/`>`, a reserved name (a built-in `uv`/`x`/`y`/`width`/`height`/
  `centre`/`E`/`PI` or input `r1`… used as a variable/formula — the validator catches this), or a
  format drift from the generator.
- **Outstanding next step:** finish the in-Flame pass (tracker:
  `documentation/live_flame_eval_progress.md`): (1) the remaining basics folders, resuming at
  `aov_tools/`; (2) **re-verify the 15 setups revoked by the 2026-07-21 bug-fix pass** — their
  GLSL changed, and since every one of those bugs had *passed* a load-check, the re-verify must
  be VISUAL (the tracker's bug-fix section says exactly what to look for per setup). Counts
  here/README can be reconciled with `/sync-docs` (the freeze is lifted and the layout is flat).
  For *more* setups, pull the next idea from `documentation/setup_expansion_backlog.md` — Tiers 1–4
  are done; only the Deferred / flagged items (and the `digital_counter` alphanumeric idea) remain.
- **Known accepted limitations (2026-07-21 review — deliberate wontfixes, don't re-litigate):**
  `voronoi_manhattan`'s 3×3 neighbourhood is insufficient for the Manhattan metric on ~0.02% of
  pixels (a 5×5 gather would ~triple the expression length — accepted); `split_tone`'s tint isn't
  perfectly luma-neutral (slight brightness shift when tinting, matches common implementations);
  `voxelize` keeps the `/n` posterize convention (top band unreachable) while
  `palette_quantize`/`zone_system_posterize` use `/(n−1)` — differing looks, both documented;
  `glsl_compile_check.py` compiles GLSL 4.10, which accepts int→float promotion (`pow(x, 2)`)
  that Flame's dialect may not — keep the always-write-decimal-literals rule; both checkers
  ignore the (always-empty) `<…Declarations>` blocks and hex literals error loudly rather than
  being supported.
