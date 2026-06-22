# lens_distort_map

**What it does:** Radial barrel/pincushion ST map (`k1`,`k2`) with anamorphic `squeeze` around Centre.

**Use case:** Add or (negate k1/k2 to) remove lens distortion — feed an STMap node.

**Inputs:** none (generator → STMap)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

**Variables:** `k1` (0.1), `k2` (0.0), `squeeze` (1.0)

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
