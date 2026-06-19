# exposure

**What it does:** Multiplies by 2^`stops`.

**Use case:** Exposure adjustment in photographic stops.

**Inputs:** Front 1

**Expects:** scene-linear

**Variables:** `stops` (0.0)

## Notes

Multiplies the image by `2^stops` — a single **photographic exposure** control. One stop is
a doubling (or halving) of light: `stops` +1 is twice as bright, -1 is half, +2 is 4x.

### Why stops (not a raw multiply)
Stops match how a DP and a lighting TD think, and they're perceptually even — every step is
the same *ratio*, so +1 looks like the same size move whether you're lifting a dark plate or
trimming a bright one. A plain "gain 1.7" carries no such intuition.

### Practical notes
- **Scene-linear only.** A clean `2^stops` multiply is only physically meaningful on linear
  light. On log/display-encoded pixels it'll crush or smear the tonal range — linearise
  first (`srgb_to_linear` or a Colour Mgmt node) and re-encode after.
- **Order:** exposure is a multiply, so it commutes with other gains but *not* with offsets
  or gamma — set exposure before `contrast` / `lift_gamma_gain` so the pivot math sees the
  intended levels.
- Keyframe `stops` for a quick exposure ramp (a light coming up, an iris pull).
