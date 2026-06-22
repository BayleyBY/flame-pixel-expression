# bayer_dither

**What it does:** Ordered 4x4 Bayer dithering: posterizes Front 1's luma to `levels` steps with a dispersed-dot threshold matrix for that crunchy retro 1-bit look.

**Use case:** Game-Boy / EGA / e-ink stylisation, retro UI, stippled gradients without banding.

**Inputs:** Front 1

**Expects:** display-referred / working image (luma-driven look)

**Variables:** `levels` (2.0), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

**Ordered (Bayer) dithering** — the retro 1-bit / limited-palette look where smooth
gradients are rendered as a fixed cross-hatch of dots instead of solid tones. Unlike random
dithering it uses a deterministic 4x4 threshold matrix, so it's stable frame-to-frame (no
crawling grain) and gives that unmistakable EGA / Game-Boy / e-ink texture.

### How it works
The 4x4 Bayer matrix is built by **index math, not a lookup table or loop**: the threshold
for a pixel is the bit-interleave of the low two bits of its x and y coordinates, scaled to
0..1 (`bv`). The pixel's luma is then quantized to `levels` steps *with that threshold added
in* before flooring — so neighbouring pixels tip over the step boundary at staggered
brightnesses, and the eye blends them into intermediate tones.

### Controls
- `levels` — number of output tones. `2.0` = pure 1-bit black/white (the iconic look);
  `3.0`-`4.0` gives a few grey steps with the dither filling the gaps.
- `aR..bB` — the two palette anchors the quantized value is mixed between (default
  black->white). Set them for a tinted duotone.

### Notes
- Expects a **display-referred / working image** (luma-driven). Set your contrast/exposure
  *before* this node — dithering is a final stylise, applied to the look you want crunched.
- For a chunkier dither, scale the image down, apply this, then scale back up (the node has
  no neighbour access, so it always dithers at native pixel pitch).
