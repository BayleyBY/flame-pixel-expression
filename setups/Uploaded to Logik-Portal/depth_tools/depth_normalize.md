# depth_normalize

**What it does:** Remaps depth `near..far` to a viewable 0..1.

**Use case:** Make a raw Z-pass viewable and prep it for the other depth tools.

**Inputs:** Matte 1 = depth

**Expects:** raw / data (no colour management)

**Variables:** `near` (0.0), `far` (1.0)

## Node dependencies
**Pipeline:** depth pass (Matte 1) → **this node**

Reads the **Z/depth pass on Matte 1** (the library convention — `m1`). Raw Z is in scene units, so set the normalising range to your near/far. No depth on Matte 1 = no useful result (input wiring is never saved in the setup file — re-wire it in Batch every time).

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Remaps a raw depth pass into a viewable, standardised **0..1** range — the front door to
the rest of the depth toolkit.

### Why run it first
Render depth (Z) usually arrives in **world units** (0 to hundreds/thousands), not 0..1. The
other depth tools default to a 0..1 range, so normalising once up front lets all their
defaults (`zMin` 0.2, `focus` 0.5, …) make sense. Set `near`/`far` to your scene's nearest
and farthest depth and the result becomes a clean 0 (near) → 1 (far) ramp.

### Practical notes
- **Depth arrives on Matte 1 (`m1`)** — the convention for every depth setup here. Wire your
  Z pass to Matte 1; view OutMatte. Also wire it to Front 1 if you want it on Result too.
- **If closer = larger** in your pass (some renderers invert Z), swap `near` and `far`.
- Depth is **raw/data** — never colour-manage it (no sRGB, no grade) before these nodes.
