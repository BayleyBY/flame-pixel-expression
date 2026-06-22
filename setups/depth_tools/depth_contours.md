# depth_contours

**What it does:** Topographic iso-depth lines every `spacing`.

**Use case:** Visualise depth structure; tech/HUD look; holdout lines.

**Inputs:** Matte 1 = depth

**Expects:** raw / data (no colour management)

**Variables:** `spacing` (0.1), `lineWidth` (0.05)

## Node dependencies
**Pipeline:** depth pass (Matte 1) → **this node**

Reads the **Z/depth pass on Matte 1** (the library convention — `m1`). Raw Z is in scene units, so set the normalising range to your near/far. No depth on Matte 1 = no useful result (input wiring is never saved in the setup file — re-wire it in Batch every time).

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Draws **topographic iso-depth lines** — a bright line every `spacing` in depth — over the
pass. Mostly a **diagnostic / look** tool: it makes the shape of a depth pass legible at a
glance, and doubles as a stylised contour effect.

### Practical notes
- **Depth on Matte 1.** `spacing` and `lineWidth` are in **depth units**, so normalise first
  (`depth_normalize`) or the lines bunch up / vanish at world-unit scales.
- Reduce `lineWidth` for fine lines; increase `spacing` for fewer of them.
