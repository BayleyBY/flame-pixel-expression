# hsv_color_replace

**What it does:** Shifts hues near `srcHue` toward `dstHue`, leaving the rest.

**Use case:** Recolour one object/colour while protecting everything else.

**Inputs:** Front 1

**Expects:** your working/display space (hue-based)

**Variables:** `srcHue` (0.33), `dstHue` (0.0), `tol` (0.06), `soft` (0.05)

## Notes

**Recolour one hue, protect the rest.** It rotates only the hue band near `srcHue` toward
`dstHue` (luma-preserving), passing everything outside the band through untouched.

### Controls
- `srcHue` = the colour to change, `dstHue` = what to change it to; `tol` = band half-width,
  `soft` = edge feather.

### Practical notes
- This is the **`dHue`-only special case** of `hsl_targeted` (which also gives saturation and
  value). Reach for it when you just need a clean hue swap on one object.
