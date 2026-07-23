# linear_to_logc

**What it does:** Linear → ARRI LogC3 (EI 800). Inverse of `logc_to_linear` (breakpoint at linear 0.010591).

**Use case:** Re-encode to LogC for delivery or to match an ARRI plate's working space.

**Inputs:** Front 1 (scene-linear)

**Expects:** scene-linear in → ARRI LogC3 (EI 800) out

_No variables._

## Notes

Inverse of `logc_to_linear` — **scene-linear → ARRI LogC3 (EI 800)**. Piecewise around the
**linear** breakpoint 0.010591 (log above, linear toe below). `log10` is `log()·0.4342944819`
with the argument guarded. Use to re-encode for delivery or to match an ARRI plate's space.

### Quick test
Numeric checkpoint: linear **0.18 → 0.391**. A linear ramp comes out lifted/flat (log
look). Pair with `logc_to_linear` for the identity round-trip check.
