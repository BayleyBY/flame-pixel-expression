# chromatic_aberration_map

**What it does:** Radial per-channel ST map (red channel's UV) + blue = offset magnitude; `amount`.

**Use case:** Lens chromatic aberration / defringe — feed an STMap node (see Notes).

**Inputs:** none (generator → STMap)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

**Variables:** `amount` (0.02)

## Notes

A **chromatic-aberration ST map** — `red = U, green = V` for a downstream **STMap node**. Output
tagged **Raw/Data**.

### The one-map limitation (read this)
A single ST map can only carry **one** source UV, but chromatic aberration needs the R/G/B
channels sampled at **different** radii. Two clean ways to wire it:

1. **Per-channel (most accurate):** this map carries the **red channel's** distorted UV (scaled
   by `1 + amount`). Build **green** with `amount = 0` (identity) and **blue** with `-amount`,
   STMap each colour channel of the plate separately, then recombine — R sampled wide, B sampled
   tight. Three instances of this node, one STMap per channel, one Channel-recombine.
2. **Magnitude-driven defringe (simplest):** ignore the per-channel UVs and use the **blue
   channel** here, which carries the **radial offset magnitude** (`length(n) * amount`). Feed
   that as the strength/mask input of a downstream **defringe / lateral-CA** node so it fringes
   strongest at the edges and zero at the optical centre.

### Controls
- **`amount`** = radial divergence (0.02 default). Use **Centre** as the optical centre.
