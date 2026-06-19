# fill_alpha

**What it does:** Sets any matte pixel above 0 to 1 (fully opaque).

**Use case:** Solidify a matte so semi-transparent areas become solid; fill key holes.

**Inputs:** Matte 1

**Expects:** any (data / value op)

_No variables._

## Notes

**Solidifies the matte** — any alpha above 0 becomes fully opaque (1.0). RGB passes through.
The rough inverse of `alpha_crunch`: where crunch removes partial alpha, fill promotes it.

### Practical notes
- Matte on **Matte 1**. Fills interior holes and semi-transparency to a solid holdout —
  handy before an erode/blur, or to turn a soft/dotty matte into a watertight one.
- It's binary (`>0 → 1`), so it won't clean stray single-pixel speckle — crunch first (or
  grade the matte) if noise is getting promoted.
