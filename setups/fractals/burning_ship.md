# burning_ship

**What it does:** Burning Ship fractal (abs-folded squaring); palette-mapped escape value.

**Use case:** Sharp, ship-like procedural fractal texture/matte.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `zoom` (400.0), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

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

### Colour / downstream
Escape value palette-mapped through `_two_color` (default black→white); **Matte** = raw 0..1
escape for masking. Identical workflow to `mandelbrot`. Blur downstream if the bands read
too hard.
