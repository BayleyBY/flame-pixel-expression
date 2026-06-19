# normal_relight

**What it does:** Lambert lighting from a normal pass and a light direction (lx,ly,lz).

**Use case:** Add or preview a CG light in comp without re-rendering.

**Inputs:** Front 1 = normal pass

**Expects:** raw normal pass in; output is scene-linear light

**Variables:** `lx` (0.0), `ly` (0.0), `lz` (1.0)

## Notes

A **Lambert (N·L) relight** from a normal pass — add or re-aim a light in comp, no re-render.
For each pixel it dots the surface normal with a light direction and clamps to 0.

### Setup
- **Front 1 = the normal pass**, components in **-1..1** (the node re-normalizes, so a
  slightly off pass is fine).
- `lx/ly/lz` = the light **direction** vector (it's normalized too; magnitude doesn't matter,
  only direction).

### Practical notes
- Output is the **diffuse term** (0..1). Multiply it onto an albedo, tint it, or add it as an
  extra light pass via `aov_grade_add` — its own RGB is a grey lighting map.
- **Normal space matters:** use a consistent space (world or camera). World-space normals give
  a light fixed in the scene; camera-space normals give a light fixed to the camera.
- Raw/data pass in; the **lit output is scene-linear** light.
