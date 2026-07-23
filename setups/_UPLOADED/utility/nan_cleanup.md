# nan_cleanup

**What it does:** Replaces NaN/Inf pixels with 0 per channel.

**Use case:** Fix corrupt render pixels that break downstream math or filters.

**Inputs:** Front 1 (optionally Front 2 as patch source)

**Expects:** any (data / value op)

_No variables._

## Notes

A **NaN / Inf scrubber** — replaces any pixel that is `isnan` or `isinf` with 0, per channel.
Renderers (and some filters) emit these, and they **poison everything downstream**: a single
NaN spreads through blurs, merges, and medians. Drop this in early as a safety net.

### The Front-2 patch variant
Instead of zeroing a bad pixel, you can **patch it from a second input**: swap the `0.0` in
each channel for `r2`/`g2`/`b2` so a NaN samples Front 2 (a clean frame, a filtered version)
at that pixel. Because the setup files are generated, make that change in `generate_setups.py`
and regenerate — don't hand-edit the `.pixel_expression_node`.

### Practical notes
- Per-channel and independent; keeps alpha (`matte = m1`). No controls in the default
  (zero-replace) form.
