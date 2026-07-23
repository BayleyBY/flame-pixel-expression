# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is
A library of **Autodesk Flame "Pixel Expression" node setups** (`.pixel_expression_node`
files) that translate the best Foundry Nuke expression-node examples into Flame's GLSL.
The Pixel Expression node (Flame 2027.1+) applies per-pixel GLSL to a clip's channels.

This repo is **public on GitHub** (`BayleyBY/flame-pixel-expression`) as of 2026-07-22 — the
old local-only rule was explicitly lifted by the user once Flame 2027.1 (the release that
ships the Pixel Expression node) came out and the verified setups went up on the **Logik
Portal** (see "Library layout" below). Committing and pushing to `origin` is normal now.

## ⭐ Library layout since the Logik Portal upload (2026-07-22)
The user uploaded the library to the Logik Portal and reorganized `setups/` by publication
status — **this layout is hand-managed by the user; do not "fix" it back to flat categories**:
- **`setups/Uploaded to Logik-Portal/`** — **112 setups, ALL verified to work in Flame 2027.1** and published
  to the Logik Portal. Sixteen folders; several categories were renamed/merged from the old
  flat layout: `alpha_matte_tools`→`matte_tools`, `sdf_shapes`→`shapes`,
  `stylization`→`stylize`, `pattern_generators`→`pattern_generator`,
  `control_surfaces`→`experimental`, and a new `just_for_fun` (the 3 fractals + `radar_sweep`
  + `digital_counter`). Cross-moves: `moire` + `sdf_lattice` → `pattern_generator`;
  `uv_transform` + `anamorphic_unsqueeze` → `stmap_generators`.
- **`setups/WORK IN PROGRESS/`** — **45 setups held back from the Portal** (`matte_combine/`
  set-ops, basic `color_grade/` ops and log-curve conversions, simple `pattern_generators/`,
  scalar `noise/`, `uv_distortion/` lens_distort/undistort, plus a few loose files at its
  root). Held back because they **either didn't appear to work in Flame or couldn't be tested
  from the docs** — a 2026-07-22 review found no GLSL bugs (mostly neutral-default /
  missing-second-input traps) and added a **"### Quick test"** block to every one of these
  `.md`s (exact wiring + values + what a working result looks like; `QUICK_TEST` table in the
  generator). The only setups whose 2026-07-21 bug-fixes were never re-verified in Flame are
  here: `radial_ramp` and `palette_quantize`.
- **One file rename:** `color_replace` → **`hsv_color_replace`** (file + md title only; the
  XML inside still says `scene/color_replace/` — proven to load fine. The generator's
  `filename` override on that setup reproduces this exactly).
- **The generator now writes in place:** `tools/generate_setups.py` indexes the current
  on-disk location of every `.pixel_expression_node` and regenerates each setup (and its
  `.md`) wherever it currently lives. Only a brand-new setup falls back to
  `setups/<category>/` — sort it into `Uploaded to Logik-Portal`/`WORK IN PROGRESS` by hand (ask the user
  where it belongs). Regeneration is verified byte-identical against the uploaded files.
- **`setups/_READY_FOR_LOGIK/`** — was the user's staging area for the **next Portal upload
  batch**. **Removed from disk 2026-07-23** (it was an empty scaffold, never visible to git);
  the user may recreate it when staging the next batch. If it reappears, it's user-managed —
  leave it alone; the in-place generator regenerates setups there like anywhere else.
- **`despill_blue` (added 2026-07-23)** — the blue-screen twin of `despill_green`. The user
  built it in Flame by modifying `despill_green` and verified it, then it was integrated into
  the generator and regenerated in place in `Uploaded to Logik-Portal/color_grade/` (the
  regenerated file differs from the user's Flame save only by whitespace in one expression).

## Commands
Generator + validator are pure-stdlib Python 3 — no deps, no venv, no install step.
- `python3 tools/generate_setups.py` — regenerate all 157 `.pixel_expression_node` files +
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
silently failed to load. The format was re-reverse-engineered from fresh Flame saves, the
generator + both checker tools were updated, and **all 156 setups were regenerated to the new
format**. See "File format facts" and "Live-Flame status" below for the delta. (The reference
saves lived in a `PR245/` folder, deleted 2026-07-22 as PR-test leftovers — recoverable from git
history at commit `9b056db` or earlier if a format question ever needs ground truth again.)
- **Regeneration is safe.** The layout is no longer flat (see "Library layout" above), but the
  generator writes each setup **in place** at its current on-disk location, so
  `tools/generate_setups.py` remains the single source of truth with no duplication risk.
- **The Live-Flame eval (reset to 0/156 by PR245) is now CLOSED** — superseded by the
  2026-07-22 Logik Portal upload: everything in `setups/Uploaded to Logik-Portal/` (now 112) is verified in Flame
  2027.1. History lives in `documentation/live_flame_eval_progress.md`.

## Golden rule: never hand-edit the setup files
`tools/generate_setups.py` is the **single source of truth**. All 157 `.pixel_expression_node`
files and their companion `.md` docs are generated from it.
- Add/change a setup → edit the `SETUPS` list, then add its `CATEGORY`, `DOCS`, and
  `EXPECTS` entries (the script warns if `DOCS`/`EXPECTS` are missing). Optionally add a
  `NOTES` entry — long-form Markdown appended to the setup's `.md` under a `## Notes`
  heading (workflow, recipes, gotchas); all 157 setups currently have one. Also add a
  `QUICK_TEST` entry (rendered as a `### Quick test` block at the end of the Notes) whenever
  a setup's working result isn't self-evident on load — exact wiring, exact values, what you
  should see; all 45 `WORK IN PROGRESS/` setups have one. A **brand-new**
  setup is written to the `setups/<category>/` fallback — move it into `Uploaded to Logik-Portal/` or
  `WORK IN PROGRESS/` by hand (the user decides which; existing setups regenerate in place).
- Regenerate: `python3 tools/generate_setups.py`
- Validate: `python3 tools/validate_setups.py` (must be **0 errors**; reserved-name
  collisions — any var/formula shadowing a built-in/input — plus undefined identifiers,
  paren problems and slot issues are all ERRORS; unused vars/formulas are warnings).
- Or just run `/sync-docs` — the project command that does regenerate + validate + drift
  check and syncs the counts and Live-Flame status across CLAUDE.md and README.
- The `.pixel_expression_node` files are XML; editing them by hand will drift from the
  generator and is almost never right.

## Key files
- `tools/generate_setups.py` — generator (SETUPS + CATEGORY + DOCS + EXPECTS + NOTES +
  QUICK_TEST tables).
- `tools/validate_setups.py` — static checker.
- `tools/glsl_compile_check.py` — optional offline GLSL compile-check (`glslangValidator`); a
  pre-Flame gate for real compile errors. Not stdlib-only — needs `brew install glslang`.
- `.claude/commands/sync-docs.md` — the `/sync-docs` project command (regenerate, validate,
  drift-check, and sync counts + Live-Flame status across the hand-maintained docs).
- `README.md` — human index (per-folder tables, colour-management, caveats).
- `setups/` — the 157 generated `.pixel_expression_node` files + companion `.md` docs, split
  by publication status: `Uploaded to Logik-Portal/` (112, verified in Flame 2027.1, on the Logik Portal, 16
  category subfolders) and `WORK IN PROGRESS/` (45 held back). See "Library layout" above.
- `documentation/pixelexpression1.pixel_expression_node` — a real Flame-saved file kept as a
  worked example of the **old pre-PR245** serialization (the original format doc was
  reverse-engineered from it; it no longer loads in the updated node — do NOT delete it. The
  *current-format* reference saves were PR-test files, deleted 2026-07-22; recover from git
  history at `9b056db` if needed). Its `.p` proxy thumbnail is gitignored — Flame regenerates
  it on load.
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

## Folders (157 setups, all under `setups/`)
**`Uploaded to Logik-Portal/` (112 — verified in Flame 2027.1, published to the Logik Portal):**
`3d_position_tools` `animated_generators` `aov_tools` `color_grade` `depth_tools`
`diagnostics` `experimental` `hsv_color` `just_for_fun` `matte_tools` `noise`
`pattern_generator` `shapes` `stmap_generators` `stylize` `utility`

**`WORK IN PROGRESS/` (45 — held back; every `.md` here has a "### Quick test" recipe):**
`color_grade` `depth_tools` `hsv_color` `matte_combine` `noise` `optics_physics`
`pattern_generators` `stylization` `uv_distortion` + 4 loose files at its root
(`box_matte`, `id_isolate`, `normal_renormalize`, `position_range_remap`).

Notes on the trickier `Uploaded to Logik-Portal/` folders:
- `just_for_fun` — the escape-time Mandelbrot/Julia/Burning-Ship (**architecture-limited to 8
  iterations**: the node has no reassignable state; the only way to iterate is the 4-formula
  chain, and inlining a complex square expands the string ~8× per step, so K=2/formula is the
  ceiling — interiors read solid, edges band; a texture tool, not a deep-zoom renderer), plus
  `radar_sweep` and `digital_counter`.
- `stmap_generators` — these OUTPUT a map (UV coords or a scalar) to be consumed by a
  **downstream node**; there is no neighbour sampling, so the gather happens elsewhere. Each
  `.md` "Notes" states the required downstream node (STMap for the UV maps; a variable-blur /
  Defocus for `coc_from_depth`/`thin_lens_coc`). Now also holds `uv_transform` and
  `anamorphic_unsqueeze` (formerly `uv_distortion/`).
- `experimental` (was `control_surfaces`) — Front 2 / Matte 2 used as a painted control
  surface (spatially-varying parameters) and the node's two-outputs-at-once trick
  (`dual_output_depth`).
- `stylize` `diagnostics` — per-pixel looks, and in-comp inspection tools (colour-blindness
  sim, exposure zebra, gamut clip).

Note: procedural noise (`noise/`) and HSV/voronoi expressions are large and built
programmatically in `tools/generate_setups.py` (the node has no user-defined GLSL functions,
so everything is inlined). All are verified in Flame, but they're the most complex GLSL in
the library — so if you edit one, they're the most likely to need a fresh live-compile check.

## Live-Flame status
- **✅ The eval is CLOSED — superseded by the Logik Portal upload (2026-07-22).** Everything in
  `setups/Uploaded to Logik-Portal/` (112 setups) **is verified to work in Flame 2027.1** and published. That
  includes 13 of the 15 setups revoked by the 2026-07-21 bug-fix pass, the fixed hue-matrix
  family (`hue_rotate`/`hsl_targeted`/`hsv_color_replace`), `normal_relight`, and the animated
  channels (`metaball_ring`; `thin_film` is in `WORK IN PROGRESS/`). The per-setup tracker
  (`documentation/live_flame_eval_progress.md`) is now historical.
- **The 45 in `setups/WORK IN PROGRESS/` were held back** because they didn't appear to work
  in Flame or couldn't be tested from their docs. A 2026-07-22 review found **no GLSL bugs**
  — the failures were wiring/default traps (OutMatte needs Matte 1; two-matte ops degrade
  with one input; grades load neutral; data tools need their pass) — and every one of these
  `.md`s now ends with a **"### Quick test"** recipe. The only bug-fixed setups never
  re-verified in Flame are `radial_ramp` and `palette_quantize` (their Quick tests say
  exactly what to confirm).
- **All 157 pass the offline checkers** (both recalibrated for the new format):
  `tools/validate_setups.py` → 0 errors/0 warnings, and `tools/glsl_compile_check.py`
  (`glslangValidator`, `#version 410 core`) → 157 compile. A clean compile is strong evidence a
  setup will load, but can't confirm Flame's exact dialect/expression-length acceptance, OutMatte
  wiring, or visual correctness — do a real load before fully trusting.
- **History/lessons (still apply):**
  - `hsl_targeted` first failed to load because it declared a variable `width` (collides with the
    injected built-in). The validator flags ANY var/formula shadowing a built-in/input — re-run it
    after edits.
  - The **PR245 break** was purely structural: the new node stores variables as a `<Variables>`
    name-keyed list + adds `<…Declarations>` blocks, and both checker tools were reading the old
    flat `Variable0..7` slots (they reported everything undefined until updated). If load/compile
    tooling suddenly reports mass-undefined identifiers after a node update, suspect a format change
    first — save a fresh setup from the node and skeleton-diff it against a known-good library file
    (method in `documentation/flame_pixel_expression_file_format.md`).
- If the user reports a load/compile failure, fix the expression in `tools/generate_setups.py`
  and regenerate — never patch the `.pixel_expression_node` directly. A silent no-error load failure
  usually means an unescaped `<`/`>`, a reserved name (a built-in `uv`/`x`/`y`/`width`/`height`/
  `centre`/`E`/`PI` or input `r1`… used as a variable/formula — the validator catches this), or a
  format drift from the generator.
- **Outstanding next steps (nothing blocking):**
  (1) **Work through `WORK IN PROGRESS/` with the new "### Quick test" recipes** — each `.md`
  now says exactly how to wire, what to set, and what a pass looks like. Setups that pass can
  be promoted (the user stages upload batches in `setups/_READY_FOR_LOGIK/`); `radial_ramp`
  and `palette_quantize` must pass their ⚠-flagged visual checks first (2026-07-21 bug-fixes,
  never eyeballed in Flame). (2) New setups from `documentation/setup_expansion_backlog.md` —
  Tiers 1–4 are done; only the Deferred / flagged items (and the `digital_counter`
  alphanumeric idea) remain. A new setup lands in the `setups/<category>/` fallback — the
  user sorts it into the layout and decides whether it gets uploaded. `/sync-docs` still
  reconciles counts/status.
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
