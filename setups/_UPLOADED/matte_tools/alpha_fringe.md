# alpha_fringe

**What it does:** Outputs `4*(1-a)*a`, which peaks at mid-grey matte values.

**Use case:** Isolate a matte's soft transition zone for edge work (despill, edge blur, light wrap).

**Inputs:** Matte 1

**Expects:** any (data / value op)

_No variables._

## Notes

**Isolates the matte's soft edge.** The expression `4 * (1 - m1) * m1` is a parabola that is
0 where alpha is 0 or 1 and peaks at **1.0 when alpha = 0.5** — so it lights up exactly the
semi-transparent transition band and ignores the solid interior and the clear exterior. RGB
passes through; the edge band is written to the matte.

### Practical notes
- Matte on **Matte 1**. Use it as a mask to confine work to the edge: light-wrap / edge
  blend, despill or de-contaminate only the fringe, or grade just the transition.
- Wider, softer mattes give a wider fringe; tighten the source matte first if the band is too
  broad.
