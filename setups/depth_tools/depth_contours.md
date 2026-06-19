# depth_contours

**What it does:** Topographic iso-depth lines every `spacing`.

**Use case:** Visualise depth structure; tech/HUD look; holdout lines.

**Inputs:** Matte 1 = depth

**Expects:** raw / data (no colour management)

**Variables:** `spacing` (0.1), `lineWidth` (0.05)

## Notes

Draws **topographic iso-depth lines** — a bright line every `spacing` in depth — over the
pass. Mostly a **diagnostic / look** tool: it makes the shape of a depth pass legible at a
glance, and doubles as a stylised contour effect.

### Practical notes
- **Depth on Matte 1.** `spacing` and `lineWidth` are in **depth units**, so normalise first
  (`depth_normalize`) or the lines bunch up / vanish at world-unit scales.
- Reduce `lineWidth` for fine lines; increase `spacing` for fewer of them.
