# gamut_clip

**What it does:** Flags illegal pixels: any channel < 0 tinted magenta, any channel > `ceiling` tinted yellow; in-range passes through. `tint` sets warning opacity.

**Use case:** Catch negative light and over-range values produced by grades, transforms or matrices.

**Inputs:** Front 1 (+ Matte 1 to render OutMatte)

**Expects:** scene-linear / your working space (negative + over-ceiling detection on raw channel values)

**Variables:** `ceiling` (1.0), `tint` (1.0)

## Notes

Flags **illegal / out-of-gamut pixels** so negative light and over-range values don't sneak
through a comp.

### How it works
- **Negative** (`min(r,g,b) < 0`) → tinted **magenta** (1,0,1).
- **Over-ceiling** (`max(r,g,b) > ceiling`, default 1.0) → tinted **yellow** (1,1,0).
- In-range pixels pass through. Negative wins where a pixel is both.
- `tint` 0..1 sets how strongly the warning colour replaces the pixel (1.0 = solid flag,
  lower = a translucent wash so you can still see the image under it).

### Controls
- `ceiling` — the upper legal bound (set to your delivery white, e.g. 1.0 for 0–1 deliverables).
- `tint` — warning opacity.

### Practical notes
- **Negative light** is the common culprit after a saturated grade, a colour-space matrix, or
  a sharpen — this makes it visible instead of silently clamped later.
- **OutMatte** is the union mask (`max(neg, over)`) — connect **Matte 1** to render it and feed
  a clamp/repair only where it's needed.
