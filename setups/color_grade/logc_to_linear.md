# logc_to_linear

**What it does:** ARRI LogC3 (EI 800) → linear. Piecewise log/linear with the standard constants (breakpoint ≈ 0.149658).

**Use case:** Linearise ARRI LogC footage for compositing/light math; re-encode with `linear_to_logc`.

**Inputs:** Front 1 (ARRI LogC3)

**Expects:** ARRI LogC3 (EI 800) in → scene-linear out

_No variables._

## Notes

**ARRI LogC3 (EI 800) → linear.** ARRI camera footage is delivered in LogC; linearise it before
light math. Piecewise: a log curve above the encoded breakpoint (≈ **0.149658**) and a linear
segment below (the toe). The LogC3 constants are baked (a fixed transform, like `srgb_to_linear`).

Pair with **`linear_to_logc`** to re-encode. **Expects** ARRI LogC3 in → scene-linear out. (LogC3
is the SUP-3.x / Alexa Classic encoding — match your source; LogC4 / other EIs differ.)
