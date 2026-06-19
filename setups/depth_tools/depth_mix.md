# depth_mix

**What it does:** Composites Front 1 (near) over Front 2 (far) at a depth threshold.

**Use case:** Insert an element at a given depth, or swap plates by distance.

**Inputs:** Front 1 + Front 2 + Matte 1 = depth

**Expects:** depth raw; plates in matching space

**Variables:** `zThresh` (0.5), `soft` (0.05)

## Notes

Composites **Front 1 (near) over Front 2 (far)** using depth as the switch — a poor-man's
deep comp for slotting one element between two layers by distance.

### Practical notes
- **Front 1 = near plate, Front 2 = far plate, Matte 1 = depth.** `zThresh` is the crossover
  depth; `soft` is the blend width across it.
- The two plates must be **aligned/registered** — this picks per-pixel between them, it
  doesn't transform anything.
- For more than two layers, chain: this node's Result becomes the next `depth_mix`'s Front 1.
