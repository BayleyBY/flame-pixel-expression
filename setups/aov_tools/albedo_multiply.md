# albedo_multiply

**What it does:** Albedo × lighting → beauty.

**Use case:** Recombine after grading albedo/texture separately (relight).

**Inputs:** Front 1 = albedo, Front 2 = lighting

**Expects:** scene-linear

_No variables._

## Notes

Multiplies a (possibly graded) **albedo** by a **lighting** pass — the recombine/relight half
of the pair with `albedo_divide`: `albedo * lighting`.

### The de-light / re-light loop
`albedo_divide` to pull lighting → grade/denoise/repaint the albedo or the lighting
independently → `albedo_multiply` to put them back together. Lets you treat texture and
illumination as separate, art-directable layers.

### Practical notes
- **Front 1 = albedo, Front 2 = lighting.**
- Both inputs **scene-linear**; the product is your reconstructed (or re-lit) beauty.
