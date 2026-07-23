# linear_to_acescct

**What it does:** Linear → ACEScct. Inverse of `acescct_to_linear` (linear breakpoint 0.0078125; `log2` branch above).

**Use case:** Encode scene-linear to ACEScct for a log grading space.

**Inputs:** Front 1 (scene-linear)

**Expects:** scene-linear (ACES) in → ACEScct out

_No variables._

## Notes

Inverse of `acescct_to_linear` — **scene-linear → ACEScct**. Piecewise around the **linear**
breakpoint 0.0078125 (`log2` branch above, linear toe below); the `log2` argument is guarded.
Transfer curve only — no primaries conversion. Use to enter an ACEScct grading space.

### Quick test
Numeric checkpoint: linear **0.18 → 0.4135**. A linear ramp comes out lifted/flat. Pair
with `acescct_to_linear` for the identity round-trip check.
