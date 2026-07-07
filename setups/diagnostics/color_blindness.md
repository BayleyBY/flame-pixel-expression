# color_blindness

**What it does:** Simulates colour-vision deficiency on Front 1 (Machado 2009 severity-1.0 matrix). `type` 0=protan / 1=deutan / 2=tritan; `amount` blends sim vs original.

**Use case:** Check that comp/graphics read for colour-blind viewers (accessibility QC).

**Inputs:** Front 1 (+ Matte 1 to pass alpha)

**Expects:** display-referred sRGB-ish (the Machado 2009 matrices are fit for sRGB display values)

**Variables:** `type` (0), `amount` (1.0)

## Notes

A **colour-blindness simulator** for accessibility QC: it shows roughly how Front 1 looks to a
viewer with one of the three dichromacies, so you can confirm graphics, mattes overlays, and
status colours still read for everyone.

### Matrices
Uses the **Machado, Oliveira & Fernandes (2009)** severity-1.0 LMS-deficiency matrices —
the same set Chrome DevTools and many accessibility tools ship — applied as a single 3×3 per
type (the LMS round-trip is pre-baked into the matrix). One matrix each for:
- `type` **0 = protanopia** (no L / red cones)
- `type` **1 = deuteranopia** (no M / green cones)
- `type` **2 = tritanopia** (no S / blue cones)

The three simulated colours are computed in parallel (formulas `simP`/`simD`/`simT`, three dot
products each), then **selected with `step()` weights** `w = (wProtan, wDeutan, wTritan)` — no
arrays or branches — and each output channel is a single `dot()` against `w`.

### Controls
- `type` picks the deficiency (round to 0/1/2; the step thresholds are at 0.5 and 1.5).
- `amount` 0..1 blends original→full simulation (handy for an A/B nudge).

### Practical notes
- **Feed display-referred, sRGB-ish values.** The matrices are fit in sRGB display space; on
  scene-linear footage add a view transform / `linear_to_srgb` before this node.
- Matte just passes **Matte 1** through; connect it if you need the alpha preserved.
