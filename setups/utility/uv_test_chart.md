# uv_test_chart

**What it does:** Generates a UV/lens calibration chart: R=U,G=V colour ramp + white grid (`gridN` cells) + red centre crosshair (`lineW` thick).

**Use case:** Sanity-check an STMap or lens warp — load it, warp it, see how the grid/UVs move.

**Inputs:** none (generator)

**Expects:** any — generates data/values

**Variables:** `gridN` (10.0), `lineW` (0.002)

## Notes

A **calibration chart generator** — the thing you run *through* an STMap or lens warp to see
what it does. The red=U / green=V colour ramp makes direction obvious, the grid shows local
stretch/squash, and the centre crosshair marks the optical centre.

### Controls
- `gridN` — grid cells across the frame.
- `lineW` — crosshair thickness (in normalised units).

### Workflow
1. Load `uv_test_chart` as a generator.
2. Send it through the **STMap / lens distort** you're testing.
3. Read the result: bent grid = distortion, colour shift = where UVs map. Pairs directly with
   `stmap_qc_overlay` (which inspects the *map itself* rather than the warped chart).
