# motion_vector_normalize

**What it does:** Rescales a pixel-unit motion-vector pass to normalized −1..1 (÷ width/height × `scale`); `pack`=1 also encodes into 0..1 for storage.

**Use case:** Convert MV units between pixels / normalized / packed for hand-off to a warp or a different app.

**Inputs:** Front 1 (motion-vector pass)

**Expects:** raw / data (a velocity pass; the math is res-dependent — see Notes)

**Variables:** `scale` (1.0), `pack` (0.0)

## Node dependencies
**Pipeline:** motion-vector pass (Front 1) → **this node** → warp/retime consumer

Reads a **2D motion-vector pass on Front 1** (`red`=u, `green`=v screen velocity), from your renderer or a vector-generator (e.g. a Motion/Kronos analysis) upstream. It's a data pass — keep it Raw/Data; colour-managing velocity corrupts it. Rescales units (pixels ↔ normalized ↔ packed) for a downstream consumer; the divide uses **this node's** width/height, so the MV pass must be at the comp resolution (or bake the size into `scale`).

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Rescales a motion-vector pass between **unit conventions**. Many MV passes are in *pixels*;
warps/retimes often want *normalized* (−1..1 = fraction of frame), and 8-bit storage wants
*packed* (0..1).

- Default (`pack`=0): outputs normalized `r/width`, `g/height`, scaled by `scale`.
- `pack`=1: also encodes into 0..1 (`×0.5+0.5`) for storage; decode later with `×2−1`.

### Resolution caveat (read this)
The divide uses **this node's** `width`/`height`. If the MV pass was authored at a different
resolution than the comp it's running in, the normalization is wrong — match resolutions, or bake
the authoring size into `scale`. **Data pass — tag Raw/Data.**
