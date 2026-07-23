# exposure_zebra

**What it does:** Overlays animated diagonal stripes on clipped pixels: per-channel max >= `hi` shows red stripes, <= `lo` shows blue stripes; mid passes through. Keyframe `phase` to crawl the stripes.

**Use case:** Spot blown highlights and crushed blacks at a glance, like a camera zebra.

**Inputs:** Front 1 (+ Matte 1 to render OutMatte)

**Expects:** scene-linear / your working space (clip thresholds hi=1.0, lo=0.0 assume normalised values)

**Variables:** `hi` (1.0), `lo` (0.0), `freq` (0.15), `phase` (0.0)

## Notes

A **camera-style zebra** overlay: animated diagonal hatching marks where Front 1 is clipping,
without changing the underlying pixels you grade against.

### How it works
- Clipping is detected on the **per-channel max**, `chmax = max(r,g,b)`: at or above `hi`
  (default 1.0) the pixel is "over" → **red** stripes; at or below `lo` (default 0.0) it is
  "under" → **blue** stripes; everything between passes through untouched.
- The stripe pattern is `step(0.0, sin((x + y) * freq + phase))` — a hard diagonal hatch.
  `freq` sets the stripe pitch; **`phase` is keyframable**, so animate it to make the stripes
  crawl (a moving hatch is easier to spot than a static one).

### Controls
- `hi` / `lo` — clip thresholds (raise `hi` to flag only true whites, etc.).
- `freq` — stripe spacing; `phase` — keyframe to crawl.

### Practical notes
- Detection is on the channel max, so a single blown channel still flags (matches how a real
  zebra warns on the brightest component).
- **OutMatte** carries the clipped mask (`max(over, under)`) — connect **Matte 1** to render
  it; use it to drive a fix downstream or just to count clipped pixels.
