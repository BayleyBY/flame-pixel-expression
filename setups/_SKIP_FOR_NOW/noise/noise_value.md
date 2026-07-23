# noise_value

**What it does:** Smooth value noise; `scale` = feature size, `gain` = contrast, `seed` = pattern/drift.

**Use case:** Organic break-up masks, soft procedural texture, displacement source.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `scale` (80), `seed` (0.0), `gain` (1.0)

## Notes

**Smooth value noise** — a single octave of interpolated lattice noise. The soft, organic
counterpart to `noise_cells`.

### Controls
- `scale` = feature size in pixels (bigger = larger blobs).
- `gain` = contrast on the result.
- `seed` = pattern selection **and** animation — keyframe it to drift/evolve (no time
  variable exists in the node).

### Practical notes
- One octave, so it's smooth but plain — reach for `noise_fbm` when you want fractal detail.
- Greyscale field on RGB, solid alpha; **tag Raw/Data**. Good base for displacement,
  soft masks, and subtle breakup.
