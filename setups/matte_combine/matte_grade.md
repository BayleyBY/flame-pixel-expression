# matte_grade

**What it does:** Gamma + gain on the matte (clamped).

**Use case:** Tighten or spread a matte's edge/density.

**Inputs:** Matte 1

**Expects:** any (data / value op)

**Variables:** `gamma` (1.0), `gain` (1.0)

## Notes

Gamma + gain on the matte, clamped. `gamma` shifts the midpoint (choke vs spread the edge),
`gain` scales density. Tightens or opens a matte's edge.
