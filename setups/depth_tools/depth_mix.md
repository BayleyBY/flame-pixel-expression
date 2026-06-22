# depth_mix

**What it does:** Composites Front 1 (near) over Front 2 (far) at a depth threshold.

**Use case:** Insert an element at a given depth, or swap plates by distance.

**Inputs:** Front 1 + Front 2 + Matte 1 = depth

**Expects:** depth raw; plates in matching space

**Variables:** `zThresh` (0.5), `soft` (0.05)

## Node dependencies
**Pipeline:** near plate (Front 1) + far plate (Front 2) + depth pass (Matte 1) → **this node**

Reads the **Z/depth pass on Matte 1** (the library convention — `m1`). Raw Z is in scene units, so set the normalising range to your near/far. No depth on Matte 1 = no useful result (input wiring is never saved in the setup file — re-wire it in Batch every time). Blends **two plates** (Front 1 near, Front 2 far) at a depth threshold.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Composites **Front 1 (near) over Front 2 (far)** using depth as the switch — a poor-man's
deep comp for slotting one element between two layers by distance.

### Practical notes
- **Front 1 = near plate, Front 2 = far plate, Matte 1 = depth.** `zThresh` is the crossover
  depth; `soft` is the blend width across it.
- The two plates must be **aligned/registered** — this picks per-pixel between them, it
  doesn't transform anything.
- For more than two layers, chain: this node's Result becomes the next `depth_mix`'s Front 1.
