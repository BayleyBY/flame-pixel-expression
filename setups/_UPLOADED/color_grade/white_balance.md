# white_balance

**What it does:** Per-channel gain (`gainR/G/B`).

**Use case:** Neutralise a colour cast or warm/cool the image.

**Inputs:** Front 1

**Expects:** scene-linear

**Variables:** `gainR` (1.0), `gainG` (1.0), `gainB` (1.0)

## Notes

A per-channel gain (`gainR` / `gainG` / `gainB`) — the simplest **colour-cast neutraliser**.
Multiplying each channel independently slides the image warm/cool/green/magenta.

### How to balance
Find something that *should* be neutral grey/white in the shot, read its RGB, and set the
gains to equalise the channels (raise the low channels or lower the high ones until R = G =
B on that sample). A common convention is to leave green at 1.0 and trim red/blue around it.

### Practical notes
- **Scene-linear** for a physically correct white balance — a channel multiply models a
  lighting/sensor gain, which is a linear operation. On display-encoded pixels it still
  *works* as a look but won't match a real temperature shift.
- It's a global cast fix; it can't correct a cast that only affects one tonal range — reach
  for `lift_gamma_gain` (per-range) or `hsl_targeted` (per-hue) for that.
- Three independent multiplies, no clamp — same downstream caution as the other grades.
