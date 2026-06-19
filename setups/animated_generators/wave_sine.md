# wave_sine

**What it does:** Horizontal scrolling sine bands; `wavelength` is the period, animated `t` drives motion.

**Use case:** Animated stripes, scanning/sweep effects, a smooth modulation source.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `wavelength` (200), `t` (animated), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

Smooth **scrolling sine bands**. Part of `animated_generators/` — motion comes from a
keyframed `t`.

### How the animation works (shared across this folder)
The node has **no time/frame variable**, so `t` is a **keyframed variable** that acts as the
clock. It ships as a 2-key channel (frame 1 → 0, frame 100 → end); **scrub frames 1–100** to
see it move. Edit those two keys to change **speed** (steeper) or **length** (move the end
frame). Here `t` runs 0 → 2 = two full cycles over the range.

### Practical notes
- `wavelength` = band period in pixels.
- Two colours `aR/aG/aB`→`bR/bG/bB` (default black→white); raw pattern on OutMatte.
