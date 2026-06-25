# wave_bounce

**What it does:** Rectified-sine bounce wave (`|sin|`) scrolling with `t`. Two-colour like the other waves.

**Use case:** Bouncing-ball motion, pulse trains, rhythmic animated bands.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `wavelength` (200), `t` (animated), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

A **rectified sine** (`|sin|`) — the wave bounces off zero each period instead of going negative,
reading like a bouncing ball or a pulse train. Part of the Cameron Carson wave set, alongside the
existing sine/triangle/square/sawtooth. **Animate `t`** (frames 1–100) to scroll it; two-colour A→B.
