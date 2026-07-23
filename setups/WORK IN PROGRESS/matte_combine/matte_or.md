# matte_or

**What it does:** Union of two mattes (`max`).

**Use case:** Combine two mattes into one.

**Inputs:** Matte 1 + Matte 2

**Expects:** any (data / value op)

_No variables._

## Notes

Union of two mattes (`max(m1, m2)`) — white where **either** is white. Inputs on Matte 1 and
Matte 2.

### Quick test
Two overlapping shapes on **Matte 1 + Matte 2** → white where **either** is. With only
Matte 1 wired it passes `m1` straight through (`m2` = 0), which looks like a no-op.
