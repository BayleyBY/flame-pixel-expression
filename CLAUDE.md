# CLAUDE.md

Guidance for working in this project.

## What this is
A library of **Autodesk Flame "Pixel Expression" node setups** (`.pixel_expression_node`
files) that translate the best Foundry Nuke expression-node examples into Flame's GLSL.
The Pixel Expression node (Flame 2027.1+) applies per-pixel GLSL to a clip's channels.

## Golden rule: never hand-edit the setup files
`tools/generate_setups.py` is the **single source of truth**. All 83 `.pixel_expression_node`
files and their companion `.md` docs are generated from it.
- Add/change a setup → edit the `SETUPS` list, then add its `CATEGORY`, `DOCS`, and
  `EXPECTS` entries (the script warns if `DOCS`/`EXPECTS` are missing). Optionally add a
  `NOTES` entry — long-form Markdown appended to the setup's `.md` under a `## Notes`
  heading (workflow, recipes, gotchas); all 83 setups currently have one.
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
- `.claude/commands/sync-docs.md` — the `/sync-docs` project command (regenerate, validate,
  drift-check, and sync counts + Live-Flame status across the hand-maintained docs).
- `README.md` — human index (per-folder tables, colour-management, caveats).
- `setups/` — the 83 generated `.pixel_expression_node` files + companion `.md` docs, in 13
  category subfolders (the loadable library).
- `documentation/pixelexpression1.pixel_expression_node` — a real Flame-saved file kept as a
  worked example of the serialization (the one the format doc was reverse-engineered from; do
  NOT delete). Its `.p` proxy thumbnail is gitignored — Flame regenerates it on load.
- `documentation/flame_pixel_expression_file_format.md` — reverse-engineered file format.
- `documentation/flame_pixel_expression_translations.md` — Nuke→Flame GLSL mapping.
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

## Reuse the generator helpers
Before writing new GLSL, check the helpers near the top of `tools/generate_setups.py`:
`DIST`/`DIST3` (distance formulas), `_two_color()`/`_COLVARS`, `_solid()` (write one expr to
RGB+Matte for a matte generator), `_HOLLOW()`, the noise builders (`_VALUE_NOISE`,
`_FBM_NOISE`, `_VORONOI`, `_vnoise_at`, `_hash2`), and the HSV/colour helpers (`HSV_P`,
`HSV_Q`, `_HUE`, `_SAT`, `_LUMA`, the `_HROT_R/G/B` hue-rotation matrix rows, `_hue_band()`,
`_hue2rgb()`). Variable budget is 8; colour vars eat 6. HSV decode (`HSV_P`+`HSV_Q`) eats 2
of the 4 formula slots.

## Folders (83 setups, all under `setups/`)
`alpha_matte_tools` `pattern_generators` `animated_generators` `color_grade`
`3d_position_tools` `depth_tools` `aov_tools` `uv_distortion` `noise` `sdf_shapes`
`hsv_color` `matte_combine` `utility`

Note: procedural noise (`noise/`) and HSV/voronoi expressions are large and built
programmatically in `tools/generate_setups.py` (the node has no user-defined GLSL functions,
so everything is inlined). All are verified in Flame, but they're the most complex GLSL in
the library — so if you edit one, they're the most likely to need a fresh live-compile check.

## Live-Flame status
- **All 83 setups are verified loading and working in Flame** (every folder, incl. the
  branchless rgb↔hsv conversions, the full `aov_tools/`/`depth_tools/`/`3d_position_tools/`/
  `uv_distortion/` sets, and `hsl_targeted` — the longest single expression in the library).
  New/changed setups still need a live check; the rest are confirmed.
- **History/lesson:** `hsl_targeted` first failed to load because it declared a variable
  `width` (collides with the injected built-in `width`); renamed to `bandWidth`. The
  validator now flags ANY var/formula that shadows a built-in/input (not just `uv`), so this
  whole silent-no-load class is caught statically — re-run `tools/validate_setups.py` after edits.
- If the user reports a load/compile failure, fix the expression in `tools/generate_setups.py`
  and regenerate — never patch the `.pixel_expression_node` directly. A silent
  no-error load failure usually means an unescaped `<`/`>` or a reserved name — a built-in
  (`uv`, `x`, `y`, `width`, `height`, `centre`, `E`, `PI`) or input (`r1`…) used as a
  variable/formula; `tools/validate_setups.py` now catches the reserved-name case.
