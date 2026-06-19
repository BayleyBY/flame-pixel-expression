# stmap

**What it does:** Generates an ST/UV map (red = U, green = V).

**Use case:** Feed an STMap node for warps/distortion, or bake screen UVs.

**Inputs:** none (generator)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

_No variables._

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
