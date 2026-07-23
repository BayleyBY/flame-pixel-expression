# matte_grade

**What it does:** Lift / gamma / gain on the matte (clamped) — same convention as `lift_gamma_gain`.

**Use case:** Tighten or spread a matte's edge/density.

**Inputs:** Matte 1

**Expects:** any (data / value op)

**Variables:** `lift` (0.0), `gamma` (1.0), `gain` (1.0)

## Notes

**Lift / gamma / gain** on the matte, clamped — the same convention as `lift_gamma_gain`
(`pow(max(m1 * gain + lift, 0), 1/gamma)`), so it behaves consistently with the RGB grade.
- `lift` — raises the black floor of the matte (offset; lifts empty areas).
- `gamma` — shifts the midpoint: `>1` spreads/opens the edge (brighter mids), `<1` chokes it.
- `gain` — scales density (multiply).

Tightens or opens a matte's edge; defaults (`lift 0 / gamma 1 / gain 1`) are neutral (pass-through).
