# wave_square

**What it does:** Scrolling hard on/off stripes; `wavelength` period, animated `t`.

**Use case:** Strobe/blink patterns, hard barcode-style wipes.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `wavelength` (200), `t` (animated), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

**Scrolling square stripes** — a hard on/off step at the half-cycle, so it's binary (no
gradient).

### Practical notes
- `wavelength` = stripe period (px); `t` is the keyframed clock (0 → 2 over frames 1–100;
  edit keys for speed/length — see `wave_sine`).
- Two colours `aR/aG/aB`→`bR/bG/bB`; raw pattern on OutMatte. Uses: shutters, barcodes,
  hard-edged wipes, blink patterns.
