# contour_lines

**What it does:** Draws topographic iso-lines from Front 1 luminance over the plate: `levels` bands, `w` line softness, `lineVal` brightness. matte = line mask.

**Use case:** Inspect a depth/luma/height field as banded contours; stylised map look.

**Inputs:** Front 1 (wire depth/height here to band it)

**Expects:** any (data / value op)

**Variables:** `levels` (10.0), `w` (0.2), `lineVal` (1.0)

## Notes

Draws **topographic iso-lines** through a scalar field — the lines trace constant-value
contours, like a map. A fast way to *see* the structure of a smooth pass (depth, a height
field, luma) that's otherwise hard to read.

### Controls
- `levels` — how many contour bands across 0..1 (more = denser lines).
- `w` — line softness. There's **no `fwidth`/derivative** here (no neighbour access), so the
  width is a fixed value in fract-space, not screen-constant — lines look slightly uneven where
  the field changes fast. That's the honest limit of a per-pixel contour.
- `lineVal` — line brightness (1 = white over the plate, 0 = black).

### Use it
Wire a **depth** or **height** pass to Front 1 to band it (drives off luminance). `matte`
carries just the line mask, so you can comp the contours over something else.
