# burning_ship

**What it does:** Burning Ship fractal (abs-folded squaring); `cRe`/`cIm` seed z0 (keyframe to morph), `gain`/`gamma` shape the bands. Grayscale.

**Use case:** Sharp, ship-like procedural fractal texture/matte.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `zoom` (400.0), `cRe` (0.0), `cIm` (0.0), `gain` (1.0), `gamma` (1.0)

## Notes

The **Burning Ship** fractal — `mandelbrot` with one change: **fold `z` to its absolute
value on each axis before squaring** (`z = vec2(abs(z.x), abs(z.y))`, then square, `+ c`).
That broken symmetry gives the sharp, hull-and-mast "ship" silhouette the name comes from.

### Same engine, same caveats
8-iteration escape-time over the 4-formula chain (each inlined step expands ~8x, so 2 per
formula is the ceiling). **Shallow and experimental** — interiors solid, edges band; a
texture tool, not a deep-zoom explorer. Pan/zoom via node **Centre** + `zoom`.

### Where the ship is
The famous structure sits down in the **negative-imaginary** region. To frame it, move the
node **Centre** below/left of the origin and raise `zoom`. Because depth is fixed at 8, the
fine antenna detail of real Burning Ship renders won't appear — you get the bold outline.

### The seed (keyframe `cRe`/`cIm`)
As in `mandelbrot`, `cRe`/`cIm` set the **starting value of `z`** (default `0,0` = the
classic Burning Ship) — the structural mirror of Julia's constant. **Keyframe them** to
distort and morph the silhouette; leave them at `(0,0)` for the familiar look.

### Output / downstream (`gain` / `gamma`)
**Grayscale** via `_solid` — escape value to RGB **and** Matte (the Matte masks). As in
`mandelbrot`, `gamma` curves the bands and `gain` scales brightness after, both default `1.0`
(`clamp(pow(escape, gamma) * gain, 0, 1)`). Identical workflow to `mandelbrot`. Blur
downstream if the bands read too hard.
