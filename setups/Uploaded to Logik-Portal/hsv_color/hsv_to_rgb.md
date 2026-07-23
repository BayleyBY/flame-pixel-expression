# hsv_to_rgb

**What it does:** Converts HSV (on Front 1 RGB) back to RGB.

**Use case:** Reconstruct colour after manipulating HSV channels.

**Inputs:** Front 1 = HSV

**Expects:** HSV data in → RGB out

_No variables._

## Node dependencies
**Pipeline:** HSV source (e.g. `rgb_to_hsv`) → **this node**

Expects an **HSV-encoded** input, which in practice comes from `rgb_to_hsv` (or another HSV source) upstream.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Converts **HSV → RGB** — the inverse of `rgb_to_hsv`. Expects Front 1 to hold **H on red, S on
green, V on blue**.

### Practical notes
- The back half of the decode → modify → encode round-trip. Hue wraps (`fract`), so values
  outside 0..1 are fine.
- Feed it the output of `rgb_to_hsv` after you've graded the H/S/V channels.
