# wave_parabolic

**What it does:** Sawtooth ramp shaped by squaring (eased parabolic ramp) scrolling with `t`. Two-colour.

**Use case:** Eased scrolling ramps, accelerating sweeps, non-linear wipe mattes.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `wavelength` (200), `t` (animated), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

A **sawtooth shaped by squaring** (`fract²`) — the ramp eases in slowly then accelerates, a
parabolic instead of linear sweep. Use it for eased scrolling ramps and non-linear wipes.
**Animate `t`** (frames 1–100) to scroll; two-colour A→B, like the other `animated_generators/`.
