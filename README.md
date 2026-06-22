# Pixel Expression Setup Library

**112 ready-to-load `.pixel_expression_node` setups** — 83 translating the best Nuke
expression examples to Flame GLSL, plus a later wave of 29 **unconventional / experimental**
setups (fractals, ST-map generators, painted control surfaces, stylization, optics/physics,
diagnostics). Load via the node's setup browser. **Connect inputs in Batch** — wiring isn't
stored in these files.

Tooling (in `tools/`):
- `tools/generate_setups.py` — single source of truth; edit a dict + the `CATEGORY` map and
  re-run to regenerate every file. Handles XML-escaping, slot padding, and folders.
- `tools/validate_setups.py` — sanity sweep: XML well-formedness, slot counts, balanced parens,
  reserved-name collisions, and undefined-identifier checks (catches variable typos).
  Run after any edit; current status: **112 setups, 0 errors, 0 warnings**.

**Live-Flame status:** the original **83 setups are confirmed loading and working in Flame** —
every folder up to `utility/`, including the branchless rgb↔hsv conversions in `hsv_color/`
and the full `aov_tools/`, `depth_tools/`, `3d_position_tools/`, and `uv_distortion/` sets.
The **29 setups in the six experimental categories** (`fractals`, `stmap_generators`,
`control_surfaces`, `stylization`, `optics_physics`, `diagnostics`) pass the validator but are
**not yet compile-checked in Flame** — load-test them before trusting. Only new or changed
setups need a re-check after editing `tools/generate_setups.py`.

Every setup also has a companion `<name>.md` next to it with **What it does / Use case /
Inputs / Expects (colour space) / Variables** — generated from the same script, so the
docs can't drift from the setups.

See `documentation/flame_pixel_expression_file_format.md` for the file format and
`documentation/flame_pixel_expression_translations.md` for the Nuke→Flame GLSL mapping.

Repo layout — the loadable library is under `setups/`, the generator/checker under `tools/`,
and reference docs under `documentation/`:

```
setups/
  alpha_matte_tools/    pattern_generators/   animated_generators/   color_grade/
  3d_position_tools/    depth_tools/          aov_tools/             uv_distortion/
  noise/                sdf_shapes/           hsv_color/             matte_combine/
  utility/
  # unconventional / experimental (not yet Flame-verified):
  fractals/             stmap_generators/     control_surfaces/      stylization/
  optics_physics/       diagnostics/
tools/         generate_setups.py  validate_setups.py
documentation/ file-format, Nuke→Flame translations, cheatsheet, node docs,
               pixelexpression1.pixel_expression_node (worked save-format example)
```

### `alpha_matte_tools/`
| File | Nuke origin | Inputs needed | Variables (defaults) |
|------|-------------|---------------|----------------------|
| `alpha_crunch` | crunch alpha | Matte 1 | `thresh` 1.0 |
| `fill_alpha` | fill alpha (>0 → 1) | Matte 1 | — |
| `alpha_fringe` | isolate matte edges | Matte 1 | — |
| `luma_key` | soft luminance key (Result + OutMatte) | Front 1 | `lo` 0.3, `hi` 0.7 |
| `difference_matte` | clip vs clean-plate diff key | Front 1 + Front 2 | `gain` 5.0 |

### `pattern_generators/`
| File | Nuke origin | Inputs needed | Variables (defaults) |
|------|-------------|---------------|----------------------|
| `radial_ramp` | radial gradient / vignette | none (uses Centre) | `radius` 600, `softness` 1.0, + colours |
| `rings` | concentric rings `sin(dist)` | none (uses Centre) | `freq` 0.05, + colours |
| `rays` | radial rays via `atan` | none (uses Centre) | `rays` 8, `rot` 0, + colours |
| `checkerboard` | checker generator | none | `size` 64, + colours |
| `bricks` | offset brick generator | none | `bw` 128, `bh` 64, + colours |
| `noise_random` | per-pixel hash noise | none | — |

**Two colours** (all except `noise_random`): the pattern blends colour **A** `aR/aG/aB`
(default black, where the pattern = 0) to colour **B** `bR/bG/bB` (default white, where it
= 1). Defaults reproduce the original grayscale; set all three of a colour equal for a
luminance-only result. OutMatte still carries the raw 0..1 pattern mask. (Numeric fields
step in tenths — use **Space + Drag** for finer colour values.)

### `animated_generators/`
Keyframed `t` variable drives motion — **scrub frames 1–100** to see it. `t` is animated
as a 2-key channel (frame 1 → 0, frame 100 → end); edit those keys to change speed/length.

| File | Nuke origin | Inputs needed | Variables (defaults) |
|------|-------------|---------------|----------------------|
| `wave_sine` | scrolling sine bands | none | `wavelength` 200, `t` 0→2 (anim), + colours |
| `wave_triangle` | scrolling triangle wave | none | `wavelength` 200, `t` 0→2 (anim), + colours |
| `wave_square` | scrolling square stripes | none | `wavelength` 200, `t` 0→2 (anim), + colours |
| `wave_sawtooth` | scrolling sawtooth ramp | none | `wavelength` 200, `t` 0→2 (anim), + colours |
| `pulse_rings` | rings expanding from Centre | none (uses Centre) | `wavelength` 100, `t` 0→2 (anim), + colours |
| `spin_rays` | rays rotating around Centre | none (uses Centre) | `rays` 8, `t` 0→1 = one turn (anim), + colours |

Two colours work exactly as in `pattern_generators/`: `aR/aG/aB` → `bR/bG/bB` (default
black→white). Defaults reproduce the original grayscale.

### `color_grade/`
| File | Nuke origin | Inputs needed | Variables (defaults) |
|------|-------------|---------------|----------------------|
| `despill_green` | green despill | Front 1 | `spill` 1.0 (0=off) |
| `saturation` | saturation grade | Front 1 | `sat` 1.0 |
| `voxelize` | posterize / quantize colour | Front 1 | `scale` 10.0 |
| `exposure` | exposure in stops (×2^stops) | Front 1 | `stops` 0.0 |
| `contrast` | contrast around a pivot | Front 1 | `contrast` 1.0, `pivot` 0.18 |
| `lift_gamma_gain` | master tonal grade | Front 1 | `lift` 0.0, `gamma` 1.0, `gain` 1.0 |
| `white_balance` | per-channel gain (cast removal) | Front 1 | `gainR/G/B` 1.0 |
| `srgb_to_linear` | sRGB → linear decode (exact) | Front 1 | — |
| `linear_to_srgb` | linear → sRGB encode (exact) | Front 1 | — |

### `3d_position_tools/`
| File | Nuke origin | Inputs needed | Variables (defaults) |
|------|-------------|---------------|----------------------|
| `pmatte_sphere` | 3D position matte | Front 1 = P-world pass | `cenR/cenG/cenB` 0, `prad` 1.0 |
| `pmatte_rings` | 3D concentric rings | Front 1 = P-world pass | `cenR/cenG/cenB` 0, `ringScale` 10 |
| `pmatte_rays` | 3D rays (X-Z plane) | Front 1 = P-world pass | `cenR/cenB` 0, `rays` 8 |
| `box_matte` | axis-aligned cube matte | Front 1 = P-world pass | `cenR/cenG/cenB` 0, `boxSize` 1.0, `soft` 0.5 |
| `normal_relight` | relight from a normal pass | Front 1 = normal pass | `lx` 0, `ly` 0, `lz` 1 |
| `fresnel_facing` | rim/edge matte from a normal pass | Front 1 = normal pass (camera-space) | `power` 2.0 |

### `depth_tools/`
**Convention: depth always arrives on Matte 1 (`m1`).** Defaults assume depth normalised
to 0..1 (`near` 0, `far` 1); for raw world-unit depth, set `near`/`far`/thresholds to your
scene range. If *closer = larger* in your pass, swap `near`/`far`. OutMatte needs Matte 1
connected (it is — depth lives there).

| File | Use | Inputs needed | Variables (defaults) |
|------|-----|---------------|----------------------|
| `depth_normalize` | remap raw depth to viewable 0..1 | Matte 1 = depth | `near` 0, `far` 1 |
| `depth_matte` | isolate a depth band → matte | Matte 1 = depth | `zMin` 0.2, `zMax` 0.6, `soft` 0.05 |
| `depth_fog` | blend beauty toward fog colour by distance | Front 1 = beauty, Matte 1 = depth | `near` 0, `far` 1, `fogR/G/B` 0.7/0.8/0.9 |
| `depth_fade` | fade colour + alpha to nothing by distance | Front 1 = beauty, Matte 1 = depth | `near` 0, `far` 1 |
| `depth_mix` | composite Front 1 (near) over Front 2 (far) | Front 1 + Front 2 + Matte 1 = depth | `zThresh` 0.5, `soft` 0.05 |
| `depth_dof_mask` | focus/defocus mask to drive a blur amount | Matte 1 = depth | `focus` 0.5, `range` 0.2 |
| `depth_contours` | topographic iso-depth lines | Matte 1 = depth | `spacing` 0.1, `lineWidth` 0.05 |
| `depth_posterize` | quantize depth into flat bands | Matte 1 = depth | `steps` 8 |
| `depth_grade` | gain ramps with distance (near→far) | Front 1 = beauty, Matte 1 = depth | `near` 0, `far` 1, `gainNear` 1.0, `gainFar` 0.3 |

### `aov_tools/`
Pairwise render-pass math. With only 2 RGB inputs, **chain nodes** to rebuild a full
beauty: each node's Result becomes the next node's Front 1 (the running sum). Light-pass
math keeps Front 1's alpha (`matte = m1`).

| File | Use | Inputs needed | Variables (defaults) |
|------|-----|---------------|----------------------|
| `aov_add` | sum two passes with per-pass gain | Front 1 + Front 2 | `gainA` 1.0, `gainB` 1.0 |
| `aov_grade_add` | tint/expose Front 2, add to Front 1 sum | Front 1 = sum, Front 2 = pass | `exposure` 1.0, `tintR/G/B` 1.0 |
| `ao_multiply` | multiply beauty by AO pass | Front 1 = beauty, Matte 1 = AO | `amount` 1.0, `aoGamma` 1.0 |
| `albedo_divide` | beauty ÷ albedo → lighting | Front 1 = beauty, Front 2 = albedo | — |
| `albedo_multiply` | albedo × lighting → beauty (relight) | Front 1 = albedo, Front 2 = lighting | — |
| `aov_clamp_negative` | remove sub-zero pixels | Front 1 | — |
| `screen_merge` | screen a glow/bloom pass onto Front 1 | Front 1 + Front 2 | `gain` 1.0 |
| `id_isolate` | grade only the region picked by an ID/mask | Front 1 = beauty, Matte 1 = mask | `gain` 1.0, `tintR/G/B` 1.0 |
| `crypto_pick_2rank` | Cryptomatte ID → matte (2 ranks) | Front 1 + Matte 1 (one crypto layer) | `id` 0.0, `tol` 0.00001 |
| `crypto_pick_4rank` | Cryptomatte ID → matte (4 ranks, cleaner AA) | Front 1 + Matte 1 + Front 2 + Matte 2 | `id` 0.0, `tol` 0.00001 |

#### Cryptomatte pickers — setup & caveats
These are *helpers*, not a full Cryptomatte node. A crypto **layer** is RGBA =
`(idHash0, coverage0, idHash1, coverage1)`. Shuffle it across this node's inputs:
- `crypto_pick_2rank`: **Front 1** = `(hash0, cov0, hash1)`, **Matte 1** = `cov1`.
- `crypto_pick_4rank`: also **Front 2** = `(hash2, cov2, hash3)`, **Matte 2** = `cov3`.

Then set `id` to the object's **float32 hash** from the Cryptomatte manifest. The picker
sums coverage across ranks whose hash matches `id` within a *relative* tolerance `tol`.

Hard requirements / limits:
- **Read the crypto pass raw** — no resize, no filtering, no colour management — or the
  hashes corrupt and nothing matches.
- **Manual hash entry.** You need the manifest value; there's no in-node eyedropper. The
  numeric field's float precision is the weak point — if a matte comes up empty, raise
  `tol` slightly; if it grabs the wrong object, lower it.
- **Rank limit.** 2 or 4 ranks only; very soft/AA edges that spill into more ranks won't be
  fully captured. For multiple objects, chain pickers and add the results.
- If your Flame has a native Cryptomatte node, prefer it; use these when it's unavailable
  or for learning.

**Beauty-rebuild example:** `aov_add` (diffuse + specular) → feed Result into `aov_grade_add`
as Front 1, with reflection as Front 2 (tint/expose it) → chain again for GI, emission, etc.
Grade any single pass in isolation by adjusting that node's variables.

### `uv_distortion/`
Generators that output a 0..1 **ST/UV map** (red = U, green = V) to feed an **STMap node** —
they don't warp the image themselves. `nx`/`ny` normalise by half-width so radial distortion
stays isotropic at any aspect ratio.

| File | Use | Inputs needed | Variables (defaults) |
|------|-----|---------------|----------------------|
| `lens_distort` | add radial barrel/pincushion | none (→ STMap) | `k1` 0.1, `k2` 0.0 |
| `lens_undistort` | remove radial distortion (approx. inverse) | none (→ STMap) | `k1` 0.1, `k2` 0.0 |
| `anamorphic_unsqueeze` | horizontal unsqueeze | none (→ STMap) | `squeeze` 2.0 |
| `uv_transform` | zoom/pan a source | none (→ STMap) | `zoom` 1.0, `panX/panY` 0.0 |

### `noise/`
Procedural noise driven by x/y (the node has no user functions, so noise is inlined).
Every generator has a **`seed`** — change it for a different pattern, or **keyframe it to
drift/evolve** the noise over time (they're no longer fixed frames).

| File | Use | Inputs needed | Variables (defaults) |
|------|-----|---------------|----------------------|
| `noise_cells` | flat random per cell | none | `cellSize` 64, `seed` 0 |
| `noise_value` | smooth value noise | none | `scale` 80, `seed` 0, `gain` 1.0 |
| `noise_fbm` | 3-octave fractal noise (clouds) | none | `scale` 80, `seed` 0, `lacunarity` 2.0, `persistence` 0.5 |
| `voronoi` | cellular / nearest-point distance | none | `scale` 80, `seed` 0, `jitter` 1.0 |

### `sdf_shapes/`
Anti-aliased shape mattes around Centre (size in px, `soft` = edge width). Centre starts
at 0,0 — use **Show Icon** to position.

| File | Use | Inputs needed | Variables (defaults) |
|------|-----|---------------|----------------------|
| `sdf_circle` | circle matte | none (uses Centre) | `radius` 200, `soft` 2 |
| `sdf_box` | rectangle matte | none (uses Centre) | `bx` 200, `by` 120, `hollow` 0, `soft` 2 |
| `sdf_rounded_box` | rounded rectangle | none (uses Centre) | `bx` 200, `by` 120, `corner` 40, `hollow` 0, `soft` 2 |
| `sdf_ring` | annulus / ring | none (uses Centre) | `radius` 200, `thickness` 20, `soft` 2 |
| `sdf_polygon` | regular n-gon | none (uses Centre) | `radius` 200, `sides` 6, `rot` 0, `hollow` 0, `soft` 2 |

`hollow` (box / rounded box / polygon): 0 = solid, increase toward 1 to cut out the middle
(outer edge stays fixed). `sdf_circle` → use `sdf_ring` for the hollow version.

### `hsv_color/`
| File | Use | Inputs needed | Variables (defaults) |
|------|-----|---------------|----------------------|
| `rgb_to_hsv` | RGB → HSV (H,S,V on R,G,B) | Front 1 | — |
| `hsv_to_rgb` | HSV → RGB | Front 1 = HSV | — |
| `hue_rotate` | luma-preserving hue shift | Front 1 | `hue` 0.0 |
| `chroma_key` | matte by hue + min saturation | Front 1 | `keyHue` 0.33, `tol` 0.05, `soft` 0.05, `satMin` 0.15 |
| `color_replace` | recolour one hue range | Front 1 | `srcHue` 0.33, `dstHue` 0.0, `tol` 0.06, `soft` 0.05 |
| `vibrance` | smart saturation (protects vivid + skin) | Front 1 | `vibrance` 0.0, `saturation` 1.0, `skinProtect` 0.0 |
| `hsl_targeted` | dHue/dSat/dVal inside one hue band | Front 1 | `centerHue` 0.33, `bandWidth` 0.08, `soft` 0.05, `dHue` 0.0, `dSat` 0.0, `dVal` 0.0 |
| `split_tone` | tint shadows vs highlights by luma | Front 1 | `shadowHue` 0.58, `highHue` 0.08, `shadowAmt` 0.1, `highAmt` 0.1, `balance` 0.0 |
| `sat_matte` | matte from a saturation window | Front 1 | `satLow` 0.15, `satHigh` 1.0, `soft` 0.05, `valMin` 0.0 |

### `matte_combine/`
| File | Use | Inputs needed | Variables (defaults) |
|------|-----|---------------|----------------------|
| `premult` | multiply RGB by matte | Front 1 + Matte 1 | — |
| `unpremult` | divide RGB by matte (guards 0) | Front 1 + Matte 1 | — |
| `matte_and` | intersection (`m1*m2`) | Matte 1 + Matte 2 | — |
| `matte_or` | union (`max`) | Matte 1 + Matte 2 | — |
| `matte_subtract` | `m1 − m2` (clamped) | Matte 1 + Matte 2 | — |
| `matte_xor` | non-overlap only | Matte 1 + Matte 2 | — |
| `matte_invert` | `1 − m1` | Matte 1 | — |
| `matte_grade` | gamma + gain on matte | Matte 1 | `gamma` 1.0, `gain` 1.0 |

### `utility/`
| File | Nuke origin | Inputs needed | Variables (defaults) |
|------|-------------|---------------|----------------------|
| `stmap` | ST/UV map `(x+0.5)/width` | none (generator) | — |
| `nan_cleanup` | NaN/Inf pixel fix | Front 1 (opt. Front 2) | — |

## Unconventional / experimental setups
The six categories below push Pixel Expression past the usual Nuke-derived toolkit: per-pixel **fractals**, **map-generators** that feed a downstream node, painted **control surfaces**, **stylization**, analytic **optics/physics**, and in-comp **diagnostics**. **These 29 setups pass `validate_setups.py` (0 errors) but are not yet compile-checked in Flame** — load-test before trusting (see the Live-Flame note at the top).

### `fractals/`
Escape-time fractals — **architecture-limited to 8 iterations** (shallow; texture, not deep-zoom).

| File | What it does | Inputs needed | Variables (defaults) |
|------|--------------|---------------|----------------------|
| `burning_ship` | Burning Ship fractal (abs-folded squaring) | none | `zoom` (400.0), + colours |
| `julia` | Escape-time Julia set | none | `zoom` (400.0), `cRe` (-0.8), `cIm` (0.156) |
| `mandelbrot` | Escape-time Mandelbrot set | none | `zoom` (400.0), + colours |

### `stmap_generators/`
Each OUTPUTS a map for a **downstream node** (STMap, or a variable-blur/Defocus for `coc_from_depth`) — see each `.md` Notes.

| File | What it does | Inputs needed | Variables (defaults) |
|------|--------------|---------------|----------------------|
| `chromatic_aberration_map` | Radial per-channel ST map (red channel's UV) + blue = offset magnitude | none (generator → STMap) | `amount` (0.02) |
| `coc_from_depth` | Per-pixel circle-of-confusion radius (0..1) from depth on Matte 1 | Matte 1 (depth) | `focusDepth` (5.0), `focusRange` (5.0), `maxBlur` (1.0) |
| `glitch_block_map` | Block-shuffle ST map | none (generator → STMap) | `blockSize` (64.0), `corruption` (0.0), `seed` (0.0) |
| `heat_haze_map` | fbm-driven UV-offset ST map | none (generator → STMap) | `scale` (120.0), `seed` (0.0), `lacunarity` (2.0), `persistence` (0.5), `amp` (0.03) |
| `kaleidoscope_map` | Mirror-folds angular space into `segments` wedges around Centre | none (generator → STMap) | `segments` (6.0), `rot` (0.0) |
| `lens_distort_map` | Radial barrel/pincushion ST map (`k1`,`k2`) with anamorphic `squeeze` around Centre. | none (generator → STMap) | `k1` (0.1), `k2` (0.0), `squeeze` (1.0) |
| `polar_to_cartesian` | Polar/rectangular ST map around Centre | none (generator → STMap) | `twist` (0.0), `zoom` (1.0) |

### `control_surfaces/`
Front 2 / Matte 2 as a painted control surface; plus the two-outputs-at-once trick.

| File | What it does | Inputs needed | Variables (defaults) |
|------|--------------|---------------|----------------------|
| `channel_pack` | Packs three single-channel signals into one RGB | Matte 1 + Matte 2 + Front 1 | — |
| `channel_unpack` | Passes a packed RGB (from channel_pack) through unchanged and routes one channel to the Matte | Front 1 (the packed RGB) | `pick` (0) |
| `dual_output_depth` | ONE node, TWO products | Front 1 (beauty) + Matte 1 (depth) | `near` (0.0), `far` (1.0), `strength` (0.0), `tintR` (0.6), `tintG` (0.8), `tintB` (1.4) |
| `painted_grade` | Grades Front 1 using a PAINTED Front 2 control map | Front 1 (image) + Front 2 (control map); Matte 1 optional (passes through) | `expRange` (2.0), `hueRange` (1.0), `satRange` (1.0) |

### `stylization/`
Per-pixel looks on Front 1 (no neighbour gather).

| File | What it does | Inputs needed | Variables (defaults) |
|------|--------------|---------------|----------------------|
| `bayer_dither` | Ordered 4x4 Bayer dithering | Front 1 | `levels` (2.0), + colours |
| `crosshatch` | Pen crosshatch | Front 1 | `spacing` (8), `lineW` (0.5), + colours |
| `crt` | CRT/VHS look | Front 1 (+ Matte 1 to pass alpha) | `scanDepth` (0.3), `maskDepth` (0.3), `vignette` (0.4), `scanFreq` (1.5), `roll` (animated) |
| `halftone` | Newspaper halftone | Front 1 | `cell` (12), `angle` (0.4), + colours |
| `palette_quantize` | Snaps Front 1 to `levels` tonal steps and tints the result between two palette anchor colours (default 4-tone | Front 1 | `levels` (4.0), + colours |
| `seven_segment` | Burns one SDF 7-segment digit (value `digit` 0..9) into the frame at Centre — no text node | none (generator; composite over your plate) | `digit` (0.0), `digScale` (150), `thick` (0.1), `hw` (0.42), `hh` (0.42), `lit` (1.0) |
| `truchet` | Truchet tiles | none (procedural; ignores Front) | `tile` (40), `lineW` (4.0), + colours |

### `optics_physics/`
Analytic physics/optics generators around Centre; animate the keyframed var noted in each `.md`.

| File | What it does | Inputs needed | Variables (defaults) |
|------|--------------|---------------|----------------------|
| `moire` | Beat pattern of two near-identical line gratings (`freqA` vs `freqB`) — an intentional moiré. | none | `freqA` (0.08), `freqB` (0.085), + colours |
| `radar_sweep` | Rotating radar/oscilloscope sweep around Centre with an exponential afterglow trailing behind the line, plus faint range rings | none (uses Centre) | `sweep` (animated), `decay` (3.0), `ringFreq` (0.02), `glowR` (0.1), `glowG` (1.0), `glowB` (0.3) |
| `starfield` | Procedural stars | none | `cellSize` (40.0), `twinkle` (animated), `threshold` (0.92), `brightness` (1.0) |
| `thin_film` | Thin-film interference iridescence | none (uses Centre) | `thickness` (1.0), `scale` (0.004), `shift` (animated) |
| `wave_interference` | Ripple-tank interference of two circular point sources (Centre + `srcX` offset) | none (uses Centre) | `srcX` (300.0), `phase` (animated), + colours |

### `diagnostics/`
In-comp inspection tools on Front 1.

| File | What it does | Inputs needed | Variables (defaults) |
|------|--------------|---------------|----------------------|
| `color_blindness` | Simulates colour-vision deficiency on Front 1 (Machado 2009 severity-1.0 matrix) | Front 1 (+ Matte 1 to pass alpha) | `type` (0), `amount` (1.0) |
| `exposure_zebra` | Overlays animated diagonal stripes on clipped pixels | Front 1 (+ Matte 1 to render OutMatte) | `hi` (1.0), `lo` (0.0), `freq` (0.15), `phase` (0.0) |
| `gamut_clip` | Flags illegal pixels | Front 1 (+ Matte 1 to render OutMatte) | `ceiling` (1.0), `tint` (1.0) |

## Colour management
The node does **no colour management** — it runs GLSL math on whatever float values arrive
at `r1/g1/b1/m1`, which depend on your project colour policy and upstream nodes. Each
setup's `.md` has an **Expects:** line; the buckets:

- **scene-linear** — physically-based light math: `exposure`, `white_balance`, AOV
  recombination (`aov_*`, `albedo_*`, `ao_multiply`, `screen_merge`), `depth_fog/fade/mix/grade`,
  `normal_relight`. Multiply/add/divide are only correct on linear light.
- **raw / data (no colour management)** — values that aren't colour: P-world, normal, and
  depth passes (`3d_position_tools`, `depth_tools`) and Cryptomatte (`crypto_pick_*`). A
  colour transform corrupts them.
- **ST/UV map output** — generators in `uv_distortion/` + `stmap`: input is irrelevant but
  the 0..1 output is data — tag it Raw/Data so no curve is applied.
- **any** — alpha math, pattern generators, cleanup ops: space-agnostic.
- **conversions** — `srgb_to_linear` / `linear_to_srgb` define their own required input.

If you work in **log or Rec.709/sRGB**, the scene-linear tools are wrong as-is: convert to
linear before them and back after (transform nodes, or the sRGB setups), and use a contrast
pivot ~0.5 instead of 0.18.

## Notes
- **Centre-based setups** (`radial_ramp`, `rings`, `rays`, `pulse_rings`, `spin_rays`)
  use `centre.x` / `centre.y`. Setups load with **Centre at 0,0** (bottom-left corner)
  and **no keyframe** — turn on **Show Icon** and drag the on-screen manipulator to
  position the effect.
- **`rings`/small values**: `freq` lives in the 0–1 range — use **Space + Drag** for
  hundredths, or it'll jump in tenths.
- **`nan_cleanup`**: replaces bad pixels with `0.0`. To patch from a clean plate
  instead, connect it to Front 2 and change `0.0` → `r2`/`g2`/`b2` per channel.
- **`pmatte_sphere`**: outputs the matte on both Result and OutMatte. Adjust
  `cenR/cenG/cenB` to the world-space point and `prad` to size.
- **Static values carry no keyframes** (Centre and static variables load as plain
  constants, Size 0); only the animated generators' `t` has keyframes. **Unused slots**
  (of the 8 variables / 4 formulas) are emitted empty (empties clear correctly on load).
- **XML-escaping (important):** comparison operators in expressions (`<`, `>`, `<=`,
  `>=`) must be written as `&lt;` / `&gt;` in the file, or it silently fails to load
  with no error. The generator handles this automatically.

- **Keyers output on Result AND OutMatte.** Confirmed: the Matte expression *can* read
  Front inputs (`r1`…). So `luma_key`, `difference_matte`, the `pmatte_*` and `box_matte`
  setups write the key to RGB **and** the Matte field — use Result or OutMatte as you like.
- **OutMatte needs Matte 1 connected.** Per Flame's docs, the OutMatte output only renders
  when a clip is on the **Matte 1** input — even when the matte expression only uses Front.
  If OutMatte is black, wire any clip into Matte 1. (Result needs only Front 1.)
- **Normal-pass setups** (`normal_relight`, `fresnel_facing`) assume a −1..1 normal pass.
  If yours is 0..1 encoded, remap first: `vec3(r1, g1, b1) * 2.0 - 1.0` (or for
  `fresnel_facing`, replace `b1` with `b1 * 2.0 - 1.0`). `fresnel_facing` also expects a
  **camera-space** normal pass (so `.z` faces the lens); world-space normals need a
  camera transform it can't do alone.

## Testing `pmatte_sphere`
A P-matte needs a position pass where RGB encode 3D coordinates. To sanity-check it
without a render: feed the **`stmap`** node into its **Front 1** (so r=0..1 across X,
g=0..1 up Y, b=0), then set `cenR` 0.5, `cenG` 0.5, `cenB` 0, `prad` 0.5 — you should
get a soft disc centred in frame. With a real P-world pass, set `cenR/cenG/cenB` to the
world point you want to isolate and `prad` to the sphere radius in world units.
