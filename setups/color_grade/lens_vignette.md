# lens_vignette

**What it does:** Physical cos⁴ lens vignette around Centre: `falloff` sets how fast it darkens (larger = gentler), `amount` mixes it in. Multiplies Front 1.

**Use case:** Natural optical edge darkening; reusable vignette for grades and look-dev.

**Inputs:** Front 1 (+ Matte 1 to pass alpha)

**Expects:** scene-linear (multiplicative falloff is correct on linear light)

**Variables:** `falloff` (800.0), `amount` (1.0)

## Notes

A **physically-motivated vignette** — natural lenses fall off as roughly **cos⁴** of the angle
from the optical axis, and that's exactly what this applies (`pow(cos(atan(r/falloff)), 4)`),
multiplied onto Front 1.

### Controls
- `falloff` — how fast it darkens, in pixels. Think of it like focal length: **larger =
  gentler** (a long lens vignettes less), smaller = heavier corners. Default 800.
- `amount` — 0..1 mix of the vignette (0 = off, 1 = full cos⁴).
- Vignette is centred on the node **Centre**, so you can offset it (decentred lens, off-axis
  light pool).

### Why cos⁴ over a radial ramp
`radial_ramp` is an arbitrary art-directable circle; this is the *optical* curve, so stacking it
on CG matches real-lens darkening and reads less like a drawn mask. **Expects scene-linear** —
a multiply is only physically right on linear light.
