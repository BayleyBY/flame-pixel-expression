# stmap

**What it does:** Generates an ST/UV map (red = U, green = V).

**Use case:** Feed an STMap node for warps/distortion, or bake screen UVs.

**Inputs:** none (generator)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

_No variables._

## Node dependencies
**Pipeline:** **this node** → **STMap**

Outputs a 0..1 **ST/UV map** (`red`=U, `green`=V) — *coordinates*, not a warped image. On its own it looks like a red/green gradient and changes nothing. Wire its output into a downstream **STMap** node's map/UV input, and the plate you want warped into the STMap's source — the STMap does the re-sample (the pixel gather this node can't do). **Tag the map Raw/Data**; colour-managing a coordinate map corrupts the warp. `stmap` is the *identity* map: warps nothing by itself — it's the baseline you offset to build a custom warp, and a handy test source for the P-matte setups.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

The **identity ST map** — `red = x/width`, `green = y/height` — i.e. each pixel's own
normalised coordinate. The baseline UV map you feed an **STMap node**.

### Why a no-op map is useful
On its own, STMapping a source through this reproduces the source unchanged (every pixel
samples itself). Its value is as a **starting point**: add offsets/expressions to red/green to
build a custom warp, or use it as a reference to sanity-check an STMap setup. The whole
`uv_distortion/` folder is specialised versions of this (lens, anamorphic, zoom/pan).

### Practical notes
- `blue` = 0, alpha = 1. **Tag the output Raw/Data** — it's coordinates, not colour, so
  colour management would corrupt the warp.

### ST-map precision (live-Flame lesson, 2026-07-23)
- **Keep the map 32-bit float end-to-end.** UV coordinates need sub-pixel precision: at
  1920 wide, adjacent pixels differ by ~0.0005 in U — the entire resolution of a 16-bit
  half float near 0.5. A 16f (or integer) map costs up to a full pixel of positional error
  and the warp comes back "correct but soft". No resize/filter/colour management on the map.
- **The STMap's sampler is generic** (typically bilinear) — visibly softer than a Transform
  node's high-quality filters on plain scaling. Prefer Transform/Resize for pure affine
  moves; an ST map earns its keep for non-uniform warps, or when several UV operations are
  composed into ONE map so the footage is resampled only once.
