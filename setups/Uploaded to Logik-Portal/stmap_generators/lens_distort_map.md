# lens_distort_map

**What it does:** Radial barrel/pincushion ST map (`k1`,`k2`) with anamorphic `squeeze` around Centre.

**Use case:** Add or (negate k1/k2 to) remove lens distortion — feed an STMap node.

**Inputs:** none (generator → STMap)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

**Variables:** `k1` (0.1), `k2` (0.0), `squeeze` (1.0)

## Node dependencies
**Pipeline:** **this node** → **STMap**

Outputs a 0..1 **ST/UV map** (`red`=U, `green`=V) — *coordinates*, not a warped image. On its own it looks like a red/green gradient and changes nothing. Wire its output into a downstream **STMap** node's map/UV input, and the plate you want warped into the STMap's source — the STMap does the re-sample (the pixel gather this node can't do). **Tag the map Raw/Data**; colour-managing a coordinate map corrupts the warp. Barrel/pincushion (`k1`,`k2`) plus an anamorphic `squeeze`; negate `k1`/`k2` to undistort.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

A **radial lens-distortion ST map** with anamorphic squeeze. `red = U, green = V`; feed it to a
downstream **STMap node** (this node → STMap **map/UV input**, plate → STMap **source input**).
Output tagged **Raw/Data** — colour-managing a coordinate map corrupts it.

### Distort vs undistort (same node)
- **`k1` is the main term:** `k1 > 0` = pincushion, `k1 < 0` = barrel. `k2` is the higher-order
  corner term.
- **To UNDISTORT, negate `k1` and `k2`** (use the opposite sign of the values you'd use to add
  the distortion). It's an approximation, so a distort→undistort round-trip won't be
  pixel-exact — match coefficients carefully and check on a grid.

### Controls
- **`squeeze`** = anamorphic X scale (2.0 = a 2x squeeze). Use Centre to set the optical centre.
- Aspect-corrected so distortion stays isotropic at any resolution.

### Typical job
Add a plate's measured distortion onto a clean CG render so it matches, or flatten a plate
(undistort), track/paint/comp, then re-distort with the same node negated.

### ST-map precision (live-Flame lesson, 2026-07-23)
- **Keep the map 32-bit float end-to-end.** UV coordinates need sub-pixel precision: at
  1920 wide, adjacent pixels differ by ~0.0005 in U — the entire resolution of a 16-bit
  half float near 0.5. A 16f (or integer) map costs up to a full pixel of positional error
  and the warp comes back "correct but soft". No resize/filter/colour management on the map.
- **The STMap's sampler is generic** (typically bilinear) — visibly softer than a Transform
  node's high-quality filters on plain scaling. Prefer Transform/Resize for pure affine
  moves; an ST map earns its keep for non-uniform warps, or when several UV operations are
  composed into ONE map so the footage is resampled only once.
