# lens_distort

**What it does:** Radial barrel/pincushion ST map (k1, k2), aspect-corrected.

**Use case:** Add lens distortion to a clean render (feed an STMap node) to match a plate.

**Inputs:** none (generator → STMap)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

**Variables:** `k1` (0.1), `k2` (0.0)

## Notes

Generates a **radial distortion ST map** (barrel / pincushion). Like everything in
`uv_distortion/`, it **does not warp the image itself** — `red = U, green = V`, and you feed
the result into an **STMap node** whose source is the plate you want distorted.

### Practical notes
- **`k1` is the main term:** `k1 < 0` = barrel (wide-angle bulge), `k1 > 0` = pincushion.
  `k2` is a higher-order term that mostly affects the far corners.
- Aspect-corrected (coords normalised by half-width), so distortion stays isotropic at any
  resolution.
- **Tag the output Raw/Data** and STMap it — colour-managing a coordinate map corrupts it.
- Typical job: **add** a plate's measured distortion onto a clean CG render so it matches.
