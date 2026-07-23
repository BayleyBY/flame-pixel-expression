# spin_rays

**What it does:** Radial rays rotating around Centre; animated `t` 0→1 is one full turn.

**Use case:** Rotating sunburst, radar sweep, hypnotic wheels.

**Inputs:** none (uses Centre)

**Expects:** any — generates data/values

**Variables:** `rays` (8), `t` (animated), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

A **rotating sunburst** — `rays` spokes turning around the node's **Centre**. The animated
cousin of `rays`.

### One turn by default
Its `t` uses the **one-cycle** keyframe (0 → 1 over frames 1–100), and `t` 0→1 maps to exactly
**one full 360° rotation** — so the default spins once across the range. Move the end key past
1 for more turns (or below for a partial sweep); reverse the keys to spin the other way.

### Practical notes
- `rays` = spoke count; Centre positions the hub.
- Two colours `aR/aG/aB`→`bR/bG/bB`; raw pattern on OutMatte. Uses: radial wipes, hypnotic /
  loading spinners, light-ray sweeps.
