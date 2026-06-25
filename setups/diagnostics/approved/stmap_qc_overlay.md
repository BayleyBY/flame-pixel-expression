# stmap_qc_overlay

**What it does:** QCs an ST/UV map on Front 1: shows the UVs, a `checkN` checker from the UV values (spot stretch), and tints pixels outside 0..1 red. matte = OOB mask.

**Use case:** Validate an ST map before an STMap warp — catch out-of-range UVs and stretching.

**Inputs:** Front 1 (an ST/UV map)

**Expects:** raw / data (Front 1 is an ST/UV coordinate map, not an image)

**Variables:** `checkN` (20.0)

## Node dependencies
**Pipeline:** ST/UV-map source (e.g. `stmap`, `lens_distort_map`, or an EXR ST layer) → **this node**

Front 1 must be an **ST/UV map** (`red`=U, `green`=V in 0..1), not an image — it reads the coordinate values directly to draw the checker and flag out-of-0..1 UVs. It **outputs a view**, not a map: park it on a monitor to inspect the map, then bypass it for the real **STMap** warp. Tag the input Raw/Data; colour-managing UVs corrupts the read.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

An **inspector for ST/UV maps** — it does **not** warp anything. Front 1 must be an ST map
(`red`=U, `green`=V in 0..1); the node visualises it so you can catch problems *before* an
STMap re-sample fails silently.

### What it shows
- The raw UVs as colour (so you see the gradient direction).
- A `checkN` checker **derived from the UV values** (not from screen position) — bunched/skewed
  squares reveal stretching the flat colours hide.
- **Red tint** wherever U or V leaves 0..1, and `matte` = that out-of-bounds mask.

### Use it / limits
Park it on a monitor, fix the map upstream, then **bypass it** for the real **STMap** warp.
It can't compute true derivatives (no neighbour access), so the checker is a *hint* at stretch,
not a Jacobian. **Tag the input Raw/Data** — colour-managing UVs corrupts the read.
