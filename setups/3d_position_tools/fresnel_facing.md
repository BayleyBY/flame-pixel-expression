# fresnel_facing

**What it does:** Rim/facing matte from a camera-space normal pass; `power` shapes the falloff.

**Use case:** Rim light, edge wear, fresnel reflections, atmosphere holdouts.

**Inputs:** Front 1 = normal pass

**Expects:** raw / data (no colour management)

**Variables:** `power` (2.0)

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
