# pmatte_rays

**What it does:** Radial rays on the X-Z plane around (cenR,cenB), `rays` count.

**Use case:** Position-based radial mask (e.g. ground fan patterns).

**Inputs:** Front 1 = P-world pass

**Expects:** raw / data (no colour management)

**Variables:** `cenR` (0), `cenB` (0), `rays` (8)

## Node dependencies
**Pipeline:** P-world pass (Front 1) → **this node** → (matte to comp)

Reads a **world-position (P) pass on Front 1** (RGB encode XYZ). Set the centre/extent variables to the world point/size you want to isolate; without a P pass it produces nothing meaningful. Tip: test without a render by feeding the `stmap` node into Front 1.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

A radial **fan of rays on the ground (X–Z) plane**, centred on a world point. It uses only
world X (`r1`) and Z (`b1`), so it's a top-down pattern — think a sunburst on the floor.

### Practical notes
- **Front 1 = P-world pass; `cenR`/`cenB` = centre X/Z in world units.** (Y is ignored — the
  pattern is constant up the vertical axis.)
- `rays` = number of spokes.
- Read the P pass raw. For rays in a different plane, you'd need a pass with the relevant two
  axes on red/blue.
