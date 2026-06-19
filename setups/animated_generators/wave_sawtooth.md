# wave_sawtooth

**What it does:** Scrolling repeating 0→1 ramp; `wavelength` period, animated `t`.

**Use case:** Scrolling gradients, phase ramps, scan lines.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `wavelength` (200), `t` (animated), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

A **scrolling sawtooth** — a repeating 0 → 1 ramp that snaps back. Great as a **phase/sweep
driver** (a value that cycles linearly) as well as a visible ramp.

### Practical notes
- `wavelength` = period (px); `t` is the keyframed clock (0 → 2 over frames 1–100; edit keys
  for speed/length — see `wave_sine`).
- Two colours `aR/aG/aB`→`bR/bG/bB`; raw pattern on OutMatte.
