# lens_undistort

**What it does:** Approximate inverse of the radial model — removes lens distortion.

**Use case:** Flatten a distorted plate before tracking/paint, then re-distort after.

**Inputs:** none (generator → STMap)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

**Variables:** `k1` (0.1), `k2` (0.0)

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
