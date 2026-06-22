# fresnel_facing

**What it does:** Rim/facing matte from a camera-space normal pass; `power` shapes the falloff.

**Use case:** Rim light, edge wear, fresnel reflections, atmosphere holdouts.

**Inputs:** Front 1 = normal pass

**Expects:** raw / data (no colour management)

**Variables:** `power` (2.0)

## Node dependencies
**Pipeline:** camera-space normal pass (Front 1) → **this node**

Reads a **normal pass on Front 1**, expected in **-1..1**. If yours is 0..1-encoded (common in EXRs), remap upstream (`*2-1`) or inline `vec3(r1,g1,b1)*2.0-1.0`. It additionally wants a **camera-space** normal (so `.z` faces the lens); world-space normals need a camera transform this node can't do.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

A **rim / facing-ratio matte** from a **camera-space** normal pass: bright where surfaces
turn away from camera (grazing angles), dark where they face it. The comp-side fresnel.

### How it works
It reads `b1` = the normal's **Z** (camera-space): 1 = facing camera, 0 = edge-on. The matte
is `(1 - Nz) ^ power`, so it peaks at the silhouette. `power` sharpens or softens the falloff.

### Practical notes
- **Camera-space normals are required** — world-space normals won't produce a view-dependent
  rim (the whole point is that it follows the camera).
- Uses for the matte: **rim light, edge wear/dirt, fresnel reflections, atmosphere on
  silhouettes.** Written to RGB **and** Matte.
- Raw/data pass in.
