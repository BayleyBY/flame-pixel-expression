# normal_renormalize

**What it does:** Restores a normal pass to unit length (`n/|n|`) after a resize/grade/lerp denormalised it; `flipG` flips green handedness (OpenGL↔DirectX).

**Use case:** Clean up a normal AOV before relighting — fix denormalised or wrong-handed normals.

**Inputs:** Front 1 (normal pass, −1..1)

**Expects:** raw / data (normal pass in −1..1)

**Variables:** `flipG` (0.0)

## Node dependencies
**Pipeline:** normal pass (Front 1) → **this node** → relight/normal consumer

Reads a **normal pass on Front 1**, expected in **-1..1**. If yours is 0..1-encoded (common in EXRs), remap upstream (`*2-1`) or inline `vec3(r1,g1,b1)*2.0-1.0`.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Normal vectors must be **unit length**, but resizing, grading, or lerping a normal AOV leaves them
denormalized — and relighting then reads wrong intensities. This divides each pixel by its length
(`n/|n|`, guarded against 0) to restore unit normals.

- `flipG` (0/1) negates green to swap **handedness** — the OpenGL ↔ DirectX green-channel
  convention that flips bump/normal lighting. Toggle it if your relight looks inverted.
- **Expects normals in −1..1.** If yours are 0..1-encoded (common in EXRs), remap upstream
  (`×2−1`) first, per the library normal convention. **Tag Raw/Data.**
