# acescct_to_linear

**What it does:** ACEScct → linear (ACES2065-style). Piecewise around the encoded breakpoint 0.155251; `exp2` branch above, linear toe below.

**Use case:** Linearise an ACEScct grading log for math, then re-encode with `linear_to_acescct`.

**Inputs:** Front 1 (ACEScct)

**Expects:** ACEScct in → scene-linear (ACES) out

_No variables._

## Notes

**ACEScct → linear (ACES).** ACEScct is the log *grading* space in an ACES pipeline (ACEScc with
a Cineon-style toe so lifts behave). Decode to linear for math, grade-bracket, or hand-off.
Piecewise around the encoded breakpoint **0.155251**: `exp2` above, a linear toe below.

Pair with **`linear_to_acescct`**. **Expects** ACEScct in → scene-linear (ACES) out. (This is the
transfer curve only — it does **not** do the AP0/AP1 primaries; handle gamut separately.)

### Quick test
Numeric checkpoint: ACEScct **0.4135 → 0.18** (18 % grey). Round-trip with
`linear_to_acescct` = identity (difference-matte black).
