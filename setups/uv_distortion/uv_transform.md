# uv_transform

**What it does:** Zoom/pan ST map; `zoom` >1 zooms in, `panX/panY` shift in UV units.

**Use case:** Reposition/scale a source through an STMap without a Transform.

**Inputs:** none (generator → STMap)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

**Variables:** `zoom` (1.0), `panX` (0.0), `panY` (0.0)

## Node dependencies
**Pipeline:** **this node** → **STMap**

Outputs a 0..1 **ST/UV map** (`red`=U, `green`=V) — *coordinates*, not a warped image. On its own it looks like a red/green gradient and changes nothing. Wire its output into a downstream **STMap** node's map/UV input, and the plate you want warped into the STMap's source — the STMap does the re-sample (the pixel gather this node can't do). **Tag the map Raw/Data**; colour-managing a coordinate map corrupts the warp. Zoom/pan a source through the STMap (`zoom`, `panX`, `panY`).

See `documentation/node_dependencies.md` for the full wiring guide.

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
