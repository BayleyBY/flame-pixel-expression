# wave_triangle

**What it does:** Scrolling triangle wave (linear up/down ramp); `wavelength` period, animated `t`.

**Use case:** Linear sweeps and sharper-than-sine modulation.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `wavelength` (200), `t` (animated), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

A **scrolling triangle wave** — a linear up/down ramp instead of a sine, so the gradient is
straight-sided with sharp peaks and troughs.

### Practical notes
- `wavelength` = period (px); `t` is the keyframed clock (0 → 2 over frames 1–100; edit the
  keys for speed/length — see `wave_sine`).
- Two colours `aR/aG/aB`→`bR/bG/bB`; raw pattern on OutMatte.
