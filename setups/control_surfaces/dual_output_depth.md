# dual_output_depth

**What it does:** ONE node, TWO products: RGB is a depth-tinted grade of the beauty (Front 1) while the Matte independently keys a depth slab via smoothstep(near, far, m1).

**Use case:** Tint the beauty by depth AND export a depth-slab matte from the same node — e.g. an atmosphere look plus a holdout for the mid-ground.

**Inputs:** Front 1 (beauty) + Matte 1 (depth)

**Expects:** depth raw on Matte 1; beauty in your working/scene-linear space

**Variables:** `near` (0.0), `far` (1.0), `strength` (0.0), `tintR` (0.6), `tintG` (0.8), `tintB` (1.4)

## Notes

A demonstration that the node makes **two products at once**: the RGB expression and the Matte
expression are independent. Here RGB carries a **depth-tinted beauty look** while the Matte
**keys a depth slab** from the same depth pass — one node, a graded image *and* a holdout
matte.

### The two outputs
- **RGB:** the beauty (Front 1) blended toward a tint (`tintR/G/B`) by depth, strength
  `strength`. Default `strength = 0.0` leaves the beauty untouched, so the look is opt-in.
- **Matte:** `smoothstep(near, far, m1)` — a soft 0..1 isolation of the depth range between
  `near` and `far`. This is computed **independently** of the RGB grade.

### Practical notes
- **Front 1 = beauty, Matte 1 = depth.** `near`/`far` are in the depth pass's own units (raw),
  so read them off your depth values; the tint is in your beauty's space.
- **OutMatte only renders when Matte 1 is connected** — which it must be here anyway, since the
  key reads `m1`.
- Swap `near`/`far` (or feed `1 - smoothstep`) to isolate *outside* the slab instead.
