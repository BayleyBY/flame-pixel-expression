# pmatte_sphere

**What it does:** Spherical matte in 3D position space around (cenR,cenG,cenB), radius `prad`.

**Use case:** Isolate a region of a CG render by world position for a local grade.

**Inputs:** Front 1 = P-world pass

**Expects:** raw / data (no colour management)

**Variables:** `cenR` (0), `cenG` (0), `cenB` (0), `prad` (1.0)

## Notes

A soft **spherical matte anchored in 3D world space** — white at a world point, falling off
to black over a world-unit radius. Because it keys off a position (P) pass, the matte sticks
to the geometry through camera moves and never aliases.

### Setup
- **Front 1 = the P-world pass** (`r = X, g = Y, b = Z` world position per pixel).
- `cenR/cenG/cenB` = the **world XYZ of the sphere centre**. To find it, sample the P pass at
  the spot you want to target and read the values. `prad` = radius in world units.

### Practical notes
- **Read the P pass raw** — no colour management, no premult; the values *are* coordinates.
- Output is a soft 0..1 ball (written to RGB **and** Matte) — drive a local grade/light with
  it, or `matte_and` it with an object alpha.
- Keyframe `cenR/G/B` to fly the region of influence through the scene.
