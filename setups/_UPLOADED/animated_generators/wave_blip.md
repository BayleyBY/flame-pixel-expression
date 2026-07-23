# wave_blip

**What it does:** A narrow spike once per period (`pow(max(sin),0)`, baked sharpness) scrolling with `t`. Two-colour.

**Use case:** Blip/pulse signals, scanning highlights, sparse rhythmic flashes.

**Inputs:** none

**Expects:** any — generates data/values

**Variables:** `wavelength` (200), `t` (animated), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

A **narrow spike** once per period — `pow(max(sin,0), 8)` keeps only the positive lobe and sharpens
it to a blip, so most of the cycle is flat with a brief flash. Sharpness is baked at 8 (raising it
would cost a variable beyond the wave family's fixed 8 slots). **Animate `t`** to send the blip
travelling; two-colour A→B.
