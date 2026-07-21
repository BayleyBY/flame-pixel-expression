# dual_output_depth

**What it does:** ONE node, TWO products: RGB is a depth-tinted grade of the beauty (Front 1) while the Matte independently keys a depth slab via smoothstep(near, far, m1).

**Use case:** Tint the beauty by depth AND export a depth-slab matte from the same node — e.g. an atmosphere look plus a holdout for the mid-ground.

**Inputs:** Front 1 (beauty) + Matte 1 (depth)

**Expects:** depth raw on Matte 1; beauty in your working/scene-linear space

**Variables:** `near` (0.0), `far` (1.0), `strength` (1.0), `tintR` (0.6), `tintG` (0.8), `tintB` (1.4)

## Node dependencies
**Pipeline:** beauty (Front 1) + depth pass (Matte 1) → **this node** → (matte to comp)

Reads the **Z/depth pass on Matte 1** (the library convention — `m1`). Raw Z is in scene units, so set the normalising range to your near/far. No depth on Matte 1 = no useful result (input wiring is never saved in the setup file — re-wire it in Batch every time). Two products from one node: RGB is a depth-tinted grade of the beauty, while OutMatte is an independent depth-slab key (needs a clip on Matte 1 for OutMatte to render).

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

A demonstration that the node makes **two products at once**: the RGB expression and the Matte
expression are independent. Here RGB carries a **depth-tinted beauty look** while the Matte
**keys a depth slab** from the same depth pass — one node, a graded image *and* a holdout
matte.

### The two outputs
- **RGB:** the beauty (Front 1) blended toward a tint (`tintR/G/B`) by depth, strength
  `strength`. Default `strength = 1.0` shows the cool depth tint on load; set it to 0 to
  pass the beauty through untouched.
- **Matte:** `smoothstep(near, far, m1)` — a soft 0..1 isolation of the depth range between
  `near` and `far`. This is computed **independently** of the RGB grade.

### Practical notes
- **Front 1 = beauty, Matte 1 = depth.** `near`/`far` are in the depth pass's own units (raw),
  so read them off your depth values; the tint is in your beauty's space.
- **OutMatte only renders when Matte 1 is connected** — which it must be here anyway, since the
  key reads `m1`.
- Swap `near`/`far` (or feed `1 - smoothstep`) to isolate *outside* the slab instead.
