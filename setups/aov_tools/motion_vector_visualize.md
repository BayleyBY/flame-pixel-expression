# motion_vector_visualize

**What it does:** Visualises a 2D motion/velocity pass (Front 1: r=u, g=v) as hue=direction, value=magnitude (`gain` scales brightness). matte = magnitude.

**Use case:** Eyeball a motion-vector pass — see direction and speed of every pixel at a glance.

**Inputs:** Front 1 (motion-vector pass)

**Expects:** raw / data (no colour management)

**Variables:** `gain` (1.0)

## Node dependencies
**Pipeline:** motion-vector pass (Front 1) → **this node**

Reads a **2D motion-vector pass on Front 1** (`red`=u, `green`=v screen velocity), from your renderer or a vector-generator (e.g. a Motion/Kronos analysis) upstream. It's a data pass — keep it Raw/Data; colour-managing velocity corrupts it. Outputs a *view* of the vectors (hue=direction, value=speed) for QC — not a usable MV pass. Park it on a monitor.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Turns an abstract **2D motion-vector pass** into something you can actually read. Front 1 holds
velocity as `red`=u, `green`=v (per-pixel screen motion). The node maps **direction → hue** (via
`atan(v, u)`) and **speed → brightness** (`|velocity|·gain`), so fast-right reads as one colour,
fast-left its opposite, and still areas go black.

### Use it
- Drop on the MV pass to QC it before a vector-blur / retime. Spot wrong-signed or zeroed regions.
- `gain` sets how much motion = full brightness — turn it up for slow shots, down for fast ones.
- `matte` carries the raw magnitude (a speed mask). **Data pass — tag Raw/Data.**
