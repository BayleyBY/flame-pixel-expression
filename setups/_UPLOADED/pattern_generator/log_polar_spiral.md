# log_polar_spiral

**What it does:** Self-similar logarithmic spiral around Centre: `arms` arm count, `freq` radial frequency, `twist` rotation (animate it). Grayscale.

**Use case:** Hypnotic spiral mattes, droste/zoom backgrounds, vortex transitions.

**Inputs:** none (uses Centre)

**Expects:** any — generates data/values

**Variables:** `freq` (8.0), `arms` (5.0), `twist` (0.0)

## Notes

A **logarithmic spiral** in log-polar coordinates: it stripes `log(radius)` against angle, so the
arms are **self-similar** — zooming in looks the same (a droste feel). `arms` = number of spiral
arms, `freq` = radial frequency (how fast the spiral winds), `twist` rotates the whole thing.

**Keyframe `twist`** for a hypnotic rotating-vortex animation. Grayscale (RGB + Matte). The radius
is guarded near the Centre so `log` never blows up. Good for transitions and energy-vortex looks.
