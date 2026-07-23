# pulse_rings

**What it does:** Concentric rings expanding from Centre over time (animated `t`).

**Use case:** Sonar/radar pulses, shockwaves, ripple triggers.

**Inputs:** none (uses Centre)

**Expects:** any — generates data/values

**Variables:** `wavelength` (100), `t` (animated), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

Concentric rings **expanding from Centre over time** — a sonar / shockwave / ripple. The
animated cousin of `rings`.

### Practical notes
- Centred on the node's **Centre** control; `wavelength` = ring spacing (px). Motion comes
  from the keyframed `t` (0 → 2 over frames 1–100), which advances the phase so rings march
  outward — edit the keys for speed/length (see `wave_sine`).
- Two colours `aR/aG/aB`→`bR/bG/bB`; raw pattern on OutMatte.
