# Node dependencies — setups that need an upstream or downstream node

Most setups in this library are self-contained: plug in a plate, get a result. But a
number of them are **one stage in a Batch graph** — they either need a *specific* output from
an upstream node wired to a *specific* input, or they emit an *intermediate* (a coordinate
map, a blur-amount map, a packed signal) that does nothing until a **downstream** node
consumes it.

This document explains every such setup and the exact wiring. It exists because three facts
about the Pixel Expression node make these dependencies easy to get wrong:

- **Input wiring is not saved in the setup file.** Loading a `.pixel_expression_node` restores
  the expression, variables and formulas — but **never** the Front/Matte connections. You wire
  Front 1 / Front 2 / Matte 1 / Matte 2 yourself in Batch every time. A setup that says it
  needs "depth on Matte 1" will silently produce garbage if you forget.
- **No neighbour sampling.** The node only ever sees the *current* pixel of each input. Any
  effect that needs to *gather* from other pixels — a real blur, a warp/displacement, a
  defocus — is **impossible inside the node**. The node can only *compute the map*; a
  downstream node does the gather. This is why the whole `uv_distortion/` and
  `stmap_generators/` families exist as map *generators*.
- **No colour management.** The node runs raw GLSL on whatever values arrive. Coordinate maps,
  depth, normals, and crypto are **data** and must not be colour-managed; light math expects
  scene-linear; display looks expect display-referred. That places implicit demands on the
  nodes *around* this one (see [Colour-management adjacency](#5-colour-management-adjacency)).

> Convention recap (see `CLAUDE.md`): depth always arrives on **Matte 1 (`m1`)**; matte-
> generating setups write to RGB **and** the Matte field; **OutMatte only renders when a clip
> is connected to Matte 1**, even if the matte expression only reads Front.

---

## Quick reference

| Setup | Folder | Needs UPSTREAM | Needs DOWNSTREAM |
|-------|--------|----------------|------------------|
| `stmap` | utility | — | **STMap** |
| `lens_distort` | uv_distortion | — | **STMap** |
| `lens_undistort` | uv_distortion | — | **STMap** |
| `anamorphic_unsqueeze` | uv_distortion | — | **STMap** |
| `uv_transform` | uv_distortion | — | **STMap** |
| `polar_to_cartesian` | stmap_generators | — | **STMap** |
| `kaleidoscope_map` | stmap_generators | — | **STMap** |
| `lens_distort_map` | stmap_generators | — | **STMap** |
| `glitch_block_map` | stmap_generators | — | **STMap** |
| `heat_haze_map` | stmap_generators | — | **STMap** |
| `chromatic_aberration_map` | stmap_generators | — | **STMap** (per-channel) |
| `coc_from_depth` | stmap_generators | depth on Matte 1 | **variable-blur / Defocus** |
| `thin_lens_coc` | stmap_generators | depth on Matte 1 | **variable-blur / Defocus** |
| `depth_dof_mask` | depth_tools | depth on Matte 1 | **variable-blur / Defocus** |
| `st_uv_map_inspector` | diagnostics | an **ST/UV map** on Front 1 | — |
| `depth_normalize` `depth_matte` `depth_contours` `depth_posterize` | depth_tools | **depth pass** on Matte 1 | (matte → comp) |
| `depth_fog` `depth_fade` `depth_grade` `depth_mix` | depth_tools | **depth pass** on Matte 1 (+ beauty/plates) | — |
| `pmatte_sphere` `pmatte_rings` `pmatte_rays` `box_matte` `position_range_remap` | 3d_position_tools | **P-world pass** on Front 1 | (matte → comp) |
| `normal_relight` `fresnel_facing` `normal_to_facing` | 3d_position_tools | **normal pass** on Front 1 (often a −1..1 remap) | — |
| `normal_renormalize` | 3d_position_tools | **normal pass** on Front 1 | a relight/normal consumer |
| `motion_vector_visualize` `motion_vector_normalize` | aov_tools | **motion-vector pass** on Front 1 | (`_normalize` → a warp/retime consumer) |
| `aov_add` `aov_grade_add` `screen_merge` | aov_tools | **two AOVs / passes** | — |
| `albedo_divide` `albedo_multiply` | aov_tools | **beauty + albedo** (or albedo + lighting) | — |
| `ao_multiply` `id_isolate` | aov_tools | **beauty + AO/ID** (AO/ID on Matte 1) | — |
| `crypto_pick_2rank` `crypto_pick_4rank` | aov_tools | **Cryptomatte ranks** (value + coverage) | — |
| `difference_matte` | alpha_matte_tools | **clean plate** on Front 2 | (matte → comp) |
| `painted_grade` | control_surfaces | **painted control map** on Front 2 | — |
| `channel_pack` | control_surfaces | four signals (2×Matte + 2×Front luma) | **`channel_unpack`** (Result + OutMatte wires) |
| `channel_unpack` | control_surfaces | packed RGB (Front 1) + ferried ch4 (Matte 1) | — |
| `dual_output_depth` | control_surfaces | beauty + depth on Matte 1 | (matte → comp) |
| `hsv_to_rgb` | hsv_color | **HSV-encoded** input (usually from `rgb_to_hsv`) | — |
| `rgb_to_hsv` | hsv_color | — | a node that reads HSV / `hsv_to_rgb` |
| `hsv_grade` | hsv_color | **HSV-encoded** input (from `rgb_to_hsv`) | **`hsv_to_rgb`** (output is HSV data) |
| `srgb_to_linear` ↔ `linear_to_srgb` | color_grade | (each is the other's inverse) | bracket linear-only ops |

Everything not listed here is self-contained (a plate or matte in, a finished result out).

---

## 1. Downstream **STMap** — coordinate-map generators

**The single most important dependency class in the library.** These setups output a 0..1
**ST/UV map** (`red = U`, `green = V`) — *coordinates*, not a warped picture. On their own they
look like a smooth red/green gradient and **do nothing to your plate**. A downstream **STMap
node** reads the map and re-samples the source at those coordinates — that re-sample (the
gather the Pixel Expression node can't do) is where the warp actually happens.

**Setups:** `stmap` · `lens_distort` · `lens_undistort` · `anamorphic_unsqueeze` ·
`uv_transform` · `polar_to_cartesian` · `kaleidoscope_map` · `lens_distort_map` ·
`glitch_block_map` · `heat_haze_map` · `chromatic_aberration_map`

### Wiring

```
[ plate to be warped ] ───────────────► Front / source input ┐
                                                              ├─► [ STMap ] ─► warped result
[ Pixel Expression: <map generator> ] ─► ST / UV map input ───┘
```

1. The Pixel Expression node's **output** goes into the STMap's **map / UV** input.
2. The **plate you want warped** goes into the STMap's **front / source** input.
3. **Tag the map Raw/Data** (no colour management). Colour-managing a coordinate map bends the
   coordinates and corrupts the warp — the classic "why is my STMap subtly wrong" bug.
4. The map should match the working **resolution/aspect**; these generators normalise by
   width/height so they're resolution-independent, but the STMap and source should agree on
   format.
5. **Keep the map 32-bit float end-to-end** (live-Flame lesson, 2026-07-23). UV coordinates
   need sub-pixel precision: at 1920 wide, adjacent pixels differ by ~0.0005 in U — the
   entire resolution of a 16-bit half float near 0.5. A 16f (or integer) map costs up to a
   full pixel of positional error and the warp comes back "correct but soft".
6. **Mind the sampler.** The STMap's resampling is generic (typically bilinear) — visibly
   softer than a Transform node's high-quality filters on plain scaling. For pure affine
   moves (unsqueeze, zoom/pan) prefer Transform/Resize; an ST map earns its keep for
   non-uniform warps, or when several UV operations compose into ONE map so the footage is
   resampled only once.

### Per-setup notes

- **`stmap`** (utility) — the identity map `(x+0.5)/width, (y+0.5)/height`. Warps nothing by
  itself; it's the *baseline* you offset to build a custom warp, and a handy test source (feed
  it into any P-matte's Front 1 to fake a position pass — see `documentation` / the README
  "Testing `pmatte_sphere`" note).
- **`lens_distort` / `lens_distort_map`** — adds barrel/pincushion. `k1 < 0` = barrel,
  `k1 > 0` = pincushion; `k2` is the corner term. `lens_distort_map` adds an anamorphic
  `squeeze`. Typical job: bake a plate's measured distortion onto a clean CG render.
- **`lens_undistort`** — the approximate inverse (remove distortion before working, re-apply
  after). It is an *approximation*; for a round-trip, undistort → work → `lens_distort` with the
  same coefficients rather than expecting a perfect inverse.
- **`anamorphic_unsqueeze`** — horizontal unsqueeze (e.g. `squeeze` 2.0 for 2× anamorphic).
- **`uv_transform`** — zoom/pan a source through the STMap (`zoom`, `panX`, `panY`).
- **`polar_to_cartesian`** — polar↔rectangular remap (tiny-planet, mirror-ball, 360 reframe).
  `twist` rotates, `zoom` scales the radius.
- **`kaleidoscope_map`** — mirror-folds angular space into `segments` wedges; `rot` spins it.
- **`glitch_block_map`** — block-shuffle / datamosh. **Keyframe `corruption`** (0→1) to trigger
  the glitch; `seed` reshuffles the block hashing.
- **`heat_haze_map`** — fbm-driven shimmer. **Keyframe `seed`** to animate the wobble; `amp`
  sets strength. (Inlines the fbm builder — the most complex GLSL here.)
- **`chromatic_aberration_map`** — *special case:* one ST map can't carry three different
  per-channel UVs. It outputs the **red** channel's UV in red/green and the **radial-offset
  magnitude** in blue. Two ways to use it:
  - **Per-channel STMap:** generate the map three times (red as-is; a green variant with
    `amount = 0`; a blue variant with `-amount`), STMap each colour channel of the plate
    separately, then recombine. Gives true R/G/B divergence. (Green is the identity, so in
    practice: two maps, two STMaps, green straight from the plate. Recombine = two small
    Pixel Expression nodes: A takes `red = r1`/`green = g2` from red-warp + plate; B takes
    A's `r1 g1` + `blue = b2` from blue-warp.) **One map on the whole plate is NOT CA** —
    all channels move together and it reads as a slight uniform zoom.
  - **Defringe input:** feed the blue (offset magnitude) into a downstream defringe/chroma
    node as its strength map. Simpler, approximate.
- **`st_uv_map_inspector`** (diagnostics) — the QC *consumer* for this whole class: wire any
  ST/UV map into its **Front 1** and it shows the UVs, a stretch-revealing checker, and tints
  out-of-0..1 pixels red (OutMatte = the out-of-bounds mask). Upstream dependency only.

---

## 2. Downstream **variable-blur / Defocus** — blur-amount maps

These output a **per-pixel blur radius** (0..1), not a blurred image — the node cannot blur
(no neighbour sampling). A downstream **variable-blur or Defocus** node uses the map as its
per-pixel blur-amount input to actually soften the plate.

**Setups:** `coc_from_depth` (stmap_generators) · `thin_lens_coc` (stmap_generators) ·
`depth_dof_mask` (depth_tools)

### Wiring

```
[ plate ] ──────────────────────────────► front input ┐
                                                        ├─► [ variable-blur / Defocus ] ─► DOF result
[ Pixel Expression: coc_from_depth ] ─► blur-amount map ┘
   ▲ depth pass on Matte 1
```

- **`coc_from_depth`** — reads the **depth pass on Matte 1** and outputs a circle-of-confusion
  radius from `focusDepth` / `focusRange` / `maxBlur`. This is an *upstream + downstream*
  setup: it needs the depth pass in, and a defocus node out. Set `focusDepth` to the depth
  value of your focal plane (sample it), `focusRange` to how quickly it falls out of focus.
- **`thin_lens_coc`** — the **physically-correct** CoC from the thin-lens equation
  (`focalLen`, `fStop`, `focusDist`, `blurScale`): background and foreground blur
  asymmetrically and far CoC saturates to a ceiling, unlike `coc_from_depth`'s linear ramp.
  Same wiring as `coc_from_depth`.
- **`depth_dof_mask`** — a simpler 0..1 in-focus/out-of-focus **mask** from depth, to drive a
  blur's matte/amount input. Use when you want to art-direct the falloff rather than model a
  physical CoC.

> Output is **data** (a blur radius / mask), so tag it Raw/Data and don't colour-manage it.

---

## 3. Upstream **render passes / AOVs** — setups that consume a specific 3D output

These need a particular **render pass or AOV** (from your renderer, an EXR's named layers, or a
Cryptomatte) wired to a specific input. Plug in the wrong pass and they fail silently. The
"upstream node" is usually a **Read/MUX/Cryptomatte/Channel** node that extracts the pass.

### Depth (depth pass → **Matte 1**)
`depth_normalize` · `depth_matte` · `depth_contours` · `depth_posterize` · `depth_fog` ·
`depth_fade` · `depth_grade` · `depth_mix` · `depth_dof_mask` · `coc_from_depth` ·
`dual_output_depth`

- Depth (Z) always arrives on **Matte 1 (`m1`)**. Raw Z is usually in scene/world units (e.g.
  0–10000), so most of these expose a normalising range — set it to your scene's near/far.
- `depth_fog` / `depth_fade` / `depth_grade` also need the **beauty** on Front 1; `depth_mix`
  needs **two plates** (Front 1, Front 2) to blend by depth.

### Position (P-world pass → **Front 1**)
`pmatte_sphere` · `pmatte_rings` · `pmatte_rays` · `box_matte` · `position_range_remap`

- These read a **world-position pass** where RGB encode XYZ. Set the centre/extent variables
  (`cenR/cenG/cenB`, `prad`, etc.) to the world point/size you want to isolate. No P pass =
  no matte. (Test without a render by feeding the `stmap` node into Front 1 — see README.)

### Normals (normal pass → **Front 1**, usually with an upstream remap)
`normal_relight` · `fresnel_facing` · `normal_to_facing` · `normal_renormalize`

- Expect a **−1..1** normal pass. If yours is **0..1 encoded** (common in EXRs), add an upstream
  remap (`*2-1`) — or do it inline (`vec3(r1,g1,b1)*2.0-1.0`). `fresnel_facing` and
  `normal_to_facing` additionally want a **camera-space** normal (so `.z` faces the lens);
  world-space normals need a camera transform this node can't do alone.
- **`normal_renormalize`** is the *repair* stage: it re-unit-lengths a filtered/resized normal
  pass, so it sits between the pass and a downstream normal consumer (relight etc.).

### Motion vectors (2D velocity pass → **Front 1**)
`motion_vector_visualize` · `motion_vector_normalize`

- Read a **2D motion-vector pass** (`red` = u, `green` = v screen velocity) from your renderer
  or a vector-generating analysis upstream. Data pass — keep it **Raw/Data**.
- `motion_vector_normalize` feeds a downstream **warp/retime consumer** that expects a specific
  vector range; `motion_vector_visualize` is a terminal inspection view (hue = direction).

### Beauty / albedo / AO / ID / Cryptomatte (AOV nodes upstream)
`albedo_divide` · `albedo_multiply` · `ao_multiply` · `aov_add` · `aov_grade_add` ·
`screen_merge` · `id_isolate` · `crypto_pick_2rank` · `crypto_pick_4rank`

- Each `.md` lists exactly which pass goes on which input (e.g. `albedo_divide`: beauty on
  Front 1, albedo on Front 2; `ao_multiply`: beauty on Front 1, AO on Matte 1). The dependency
  is on the **renderer/AOV pipeline** delivering those layers.
- **`crypto_pick_2rank` / `crypto_pick_4rank`** are the most upstream-dependent: they need
  **Cryptomatte rank layers** — value on a Front, coverage on the matching Matte (2-rank uses
  Front 1 + Matte 1; 4-rank adds Front 2 + Matte 2). You extract those ranks upstream
  (Cryptomatte/Channel node) before this node can pick an ID.

---

## 4. Upstream **a clean plate, a painted map, or a sibling setup**

### A clean plate on Front 2
- **`difference_matte`** — keys what *changed* between a shot (Front 1) and a **clean plate**
  (Front 2). Needs the aligned clean plate wired upstream; `gain` scales the difference.

### A painted control map on Front 2
- **`painted_grade`** — `r2` drives local exposure, `g2` local hue, `b2` local saturation. The
  upstream "node" is wherever you **paint/generate that control map**: a Paint node, a roto
  fill, a ramp, or even another Pixel Expression generator. Flat 0.5 grey = neutral.

### Paired Pixel Expression nodes (rely on a sibling of this library)
- **`channel_pack` → `channel_unpack`** — `channel_pack` ferries **four** single-channel
  signals on its Result + OutMatte wire pair (red = Matte 1, green = Matte 2, blue = Front 1
  luma; OutMatte = Front 2 luma — the Result socket is RGB-only, so channel 4 rides the
  OutMatte). Run both wires to `channel_unpack` (Result → Front 1, OutMatte → Matte 1 — that
  second wire doubles as the OutMatte-enabler its docs used to require anyway); `pick` =
  0/1/2/3 recovers any of the four. Leave the pack's Front 2 empty for the old 3-wide
  behaviour. Useless apart — they're a **matched pair** across a comp.
- **`rgb_to_hsv` ↔ `hsv_to_rgb`** — `hsv_to_rgb` expects an **HSV-encoded** image, which in
  practice comes from `rgb_to_hsv` (or another HSV source) upstream. Use them to bracket a
  hand-built HSV operation when one of the dedicated `hsv_color/` setups doesn't fit.
  `hsv_grade` is the library's ready-made middle for this sandwich
  (`rgb_to_hsv` → `hsv_grade` → `hsv_to_rgb`): wrapping hue shift, saturation gain + gamma,
  value gain + gamma, all on the raw H/S/V channels. Its S output is clamped to 0..1 (an
  over-range S makes the decode extrapolate to negative RGB); V is left unclamped, so follow
  the sandwich with `hue_preserving_clip` for a delivery clamp.
- **`srgb_to_linear` ↔ `linear_to_srgb`** — an encode/decode pair. Reach for them only when you
  *can't* use a proper OCIO/colour-management node; they're a convenience, not a replacement
  for your colour pipeline.

---

## 5. Colour-management adjacency

The node does **no colour management**, so for many setups the *correct result depends on what
colour space the surrounding nodes hand it*. This is a soft "upstream/downstream" dependency on
your **view transform / OCIO / colour-space** nodes. Each setup's `.md` has an **Expects:** line;
the ones that care:

- **Light/energy math → scene-linear:** `exposure`, `white_balance`, `aov_add`,
  `aov_grade_add`, `albedo_multiply`, `screen_merge`, `normal_relight` (output), etc. Feed them
  linear; if you're in log/display, convert upstream.
- **Display looks → display-referred:** the `stylization/` looks generally read best on a
  display-referred/working image — apply a view transform upstream. (`color_blindness` is a
  special case: the Machado matrices are **derived in linear RGB**; running them on
  display-encoded sRGB is the common QC approximation — see its `.md`.)
- **Pure data → no management:** all ST/UV maps, depth, P, normals, Cryptomatte, `coc_from_depth`.
  **Tag Raw/Data and keep them out of the colour pipeline** both up- and downstream.
- **Contrast/pivot tools** (`contrast`) assume a pivot (0.18 in linear, ~0.5 in display) — set
  it to match the space the upstream node delivers.

See the **Colour management** section of `README.md` for the full per-space guidance.

---

## How to keep this document accurate

This is a **hand-maintained** guide (like `README.md`), not generated. The source of truth for
each setup's inputs and downstream notes is its companion `.md` (and the `DOCS`/`EXPECTS`/`NOTES`
tables in `tools/generate_setups.py`). If you add or change a setup that depends on another node,
update its `.md` (via the generator) **and** add/adjust its row here.
