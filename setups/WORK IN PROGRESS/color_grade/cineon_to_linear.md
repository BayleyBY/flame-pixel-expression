# cineon_to_linear

**What it does:** Kodak Cineon/DPX log → linear. `blackPt`/`whitePt` (10-bit code values 95/685) and `gammaC` (0.6) define the curve; maps blackPt→0, whitePt→1.

**Use case:** Linearise scanned-film / DPX log plates before doing light math, then re-encode with `linear_to_cineon`.

**Inputs:** Front 1 (Cineon-log, normalised 0..1)

**Expects:** Cineon/DPX log in → scene-linear out (the transform defines the spaces)

**Variables:** `blackPt` (95.0), `whitePt` (685.0), `gammaC` (0.6)

## Notes

The **Kodak Cineon / DPX log → linear** decode — the classic film-scan linearisation (Nuke's
`Log2Lin`). Scanned-negative and DPX plates are stored in **printing-density log**; you must
linearise before any light math (grades, merges, blurs) or the results are wrong.

### Controls
- `blackPt` / `whitePt` — the 10-bit code values that map to 0.0 and 1.0 (defaults **95 / 685**,
  the Cineon standard). `r1` is the code value normalised to 0..1.
- `gammaC` — the density slope (default **0.6**).
- The `fb` formula is the black-point floor so `blackPt`→0 and `whitePt`→1 exactly.

### Pairing
Bracket film-log work with `cineon_to_linear` … *(do your linear ops)* … **`linear_to_cineon`**
to round-trip back to DPX. **Expects** a Cineon-log input; tag the linear output scene-linear.

### Quick test
Feed a horizontal 0–1 ramp: output holds near 0 until input ≈ **0.093** (code 95 = blackPt
→ 0.0) and reaches **1.0 at ≈ 0.67** (code 685 = whitePt), continuing into super-white
above. On a real DPX/log plate: the milky log look snaps to contrasty linear with deep
shadows.
