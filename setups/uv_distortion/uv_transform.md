# uv_transform

**What it does:** Zoom/pan ST map; `zoom` >1 zooms in, `panX/panY` shift in UV units.

**Use case:** Reposition/scale a source through an STMap without a Transform.

**Inputs:** none (generator → STMap)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

**Variables:** `zoom` (1.0), `panX` (0.0), `panY` (0.0)

## Notes

A zoom / pan **ST map** — repositions a source through an STMap node instead of a Transform.
Outputs `red = U, green = V`.

### Why do it as an ST map
When your pipeline is already STMap-based (lens work, warps), folding a reposition into the
same map keeps everything to a **single resample** and a single coordinate space, rather than
stacking a separate Transform.

### Practical notes
- **`zoom` > 1 zooms in**, < 1 out (centred). `panX`/`panY` shift in **UV units** (0..1 across
  the frame), so 0.1 = a tenth of the width/height.
- **Tag the output Raw/Data** and STMap it onto the source.
