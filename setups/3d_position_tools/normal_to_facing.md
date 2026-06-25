# normal_to_facing

**What it does:** Facing/rim ratio from a view-space normal pass (Front 1): `rim` 0=facing (toward camera), 1=rim (edges), `falloff` shapes it. Result on RGB + Matte.

**Use case:** Rim/edge mattes or a facing key when only a normal AOV (not P) is available.

**Inputs:** Front 1 (view-space normal)

**Expects:** raw / data (view-space normal pass in −1..1)

**Variables:** `rim` (0.0), `falloff` (1.0)

## Node dependencies
**Pipeline:** view-space normal pass (Front 1) → **this node**

Reads a **normal pass on Front 1**, expected in **-1..1**. If yours is 0..1-encoded (common in EXRs), remap upstream (`*2-1`) or inline `vec3(r1,g1,b1)*2.0-1.0`. Must be **view/camera-space** normals — a world-space pass won't give a camera-relative facing ratio.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

A **facing ratio** straight from a normal AOV — the dot of the (view-space) normal with the camera
axis, which here is just the **Z (blue) channel**. `fresnel_facing` does this from a P pass; this
is for when you only have a normal pass.

- `rim`=0 → facing (surfaces pointing at camera = white); `rim`=1 → rim (edges/grazing = white).
- `falloff` shapes the curve (a power) — raise it to tighten the rim to a thin edge.
- Result is written to RGB **and** Matte. **Only valid for view/camera-space normals** — a
  world-space normal pass won't give a camera-relative facing. **Tag Raw/Data.**
