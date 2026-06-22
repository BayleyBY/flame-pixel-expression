# pmatte_rings

**What it does:** Concentric 3D shells around the centre point, spacing `ringScale`.

**Use case:** Position-based ring patterns or masks on CG geometry.

**Inputs:** Front 1 = P-world pass

**Expects:** raw / data (no colour management)

**Variables:** `cenR` (0), `cenG` (0), `cenB` (0), `ringScale` (10.0)

## Node dependencies
**Pipeline:** P-world pass (Front 1) → **this node** → (matte to comp)

Reads a **world-position (P) pass on Front 1** (RGB encode XYZ). Set the centre/extent variables to the world point/size you want to isolate; without a P pass it produces nothing meaningful. Tip: test without a render by feeding the `stmap` node into Front 1.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Concentric **3D rings** (a sine of world distance) radiating from a world point — like
`pmatte_sphere`, but a repeating ripple instead of a single falloff.

### Practical notes
- **Front 1 = P-world pass; `cenR/cenG/cenB` = centre in world XYZ** (read from the P pass).
- `ringScale` sets the ring frequency (higher = tighter rings).
- World-anchored, so the rings cling to the geometry — handy for **shockwaves / ripples /
  energy pulses** emanating from a point. Keyframe `cenR/G/B` or `ringScale` to animate.
- Read the P pass raw.
