# lens_undistort

**What it does:** Approximate inverse of the radial model — removes lens distortion.

**Use case:** Flatten a distorted plate before tracking/paint, then re-distort after.

**Inputs:** none (generator → STMap)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

**Variables:** `k1` (0.1), `k2` (0.0)

## Node dependencies
**Pipeline:** **this node** → **STMap**

Outputs a 0..1 **ST/UV map** (`red`=U, `green`=V) — *coordinates*, not a warped image. On its own it looks like a red/green gradient and changes nothing. Wire its output into a downstream **STMap** node's map/UV input, and the plate you want warped into the STMap's source — the STMap does the re-sample (the pixel gather this node can't do). **Tag the map Raw/Data**; colour-managing a coordinate map corrupts the warp. Approximate *inverse* of `lens_distort`. For a clean round-trip, undistort → work → re-apply `lens_distort` with the same coefficients rather than trusting a perfect inverse.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

The **approximate inverse** of `lens_distort` — same radial polynomial, but it divides where
distort multiplies. Outputs an ST map to feed an STMap node.

### The undistort → work → redistort workflow
Flatten a distorted plate (so straight lines are straight) → **track / paint / roto / add CG**
on the undistorted plate → re-apply the distortion with `lens_distort` using the **same
`k1`/`k2`** so the result drops back onto the original.

### Practical notes
- It's an **approximation** (a true inverse of the polynomial has no closed form), so a
  distort→undistort round-trip won't be pixel-exact — fine for most work, but match `k1`/`k2`
  carefully and check edges on a grid.
- **Tag the output Raw/Data** and STMap it.
