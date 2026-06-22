# mandelbrot

**What it does:** Escape-time Mandelbrot set; 0..1 smooth escape value palette-mapped (aR..bB).

**Use case:** Procedural fractal texture/matte; abstract background or displacement source.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `zoom` (400.0), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

A real **escape-time Mandelbrot** computed per pixel — but a deliberately **shallow,
experimental** one, not a deep-zoom renderer. Read the architecture note below before you
judge the image.

### Why it's shallow (the architecture limit)
The node has **no reassignable state** — you can't write a loop that updates `z`. The only
way to iterate is the **4-formula chain**: `z0` does a couple of inlined steps from the
seed, `z1` references `z0` by name and does a couple more, … through `z3`. A complex square
references `z` several times, so each inlined step **expands the expression text by ~8x**.
That caps us at **2 iterations per formula = 8 total** before the string blows past the
node's practical size limit (K=3 would be ~33 KB per formula). So:
- **Interiors read solid** (they never escape in 8 iterations).
- **Edges band** in a few discrete rings rather than the infinitely fine filigree you'd get
  from hundreds of iterations.
- This is a **texture/abstract-pattern** tool, not a fractal explorer.

### How it works
Each pixel maps to the complex plane relative to the node **Centre**, scaled by `zoom`
(bigger `zoom` = closer). `c` = that coordinate, `z` starts at 0. Every iteration squares
`z` and adds `c`, and accumulates `step(|z|^2, 4.0)` — 1 while still inside the bailout
radius, 0 once it escapes. Summing across all 8 iterations gives a 0..1 **smooth escape
value** (`z3.z / 20.0`, normalised to the *maximum possible* count so the tonal range stays
stable even though only 8 steps run).

### Pan / zoom
- **Pan:** move the node **Centre** to the region you want centred.
- **Zoom:** raise `zoom` (default 400). Because iteration depth is fixed at 8, zooming in
  past a point just shows bigger, smoother bands — there's no new detail to reveal.

### Colour
The escape value is palette-mapped through `_two_color` (`aR/aG/aB` → `bR/bG/bB`, default
black→white). Set the two colours for a duotone fractal; the **Matte** holds the raw 0..1
escape value for masking. The classic black-interior / coloured-exterior look is the default.

### Downstream
Pure generator (no inputs). Feed the Matte into a comp as a procedural mask, or the RGB as a
background / displacement source. Pair with a **Blur** if the discrete bands read too hard.
