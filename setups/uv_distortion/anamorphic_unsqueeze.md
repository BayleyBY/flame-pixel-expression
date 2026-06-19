# anamorphic_unsqueeze

**What it does:** Horizontal stretch ST map; `squeeze` = anamorphic factor (2.0 = 2x).

**Use case:** Unsqueeze anamorphic footage to its correct aspect.

**Inputs:** none (generator → STMap)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

**Variables:** `squeeze` (2.0)

## Notes

A horizontal-stretch **ST map** to un-squeeze anamorphic footage back to its true aspect.
Outputs `red = U, green = V`; feed it to an STMap node.

### Practical notes
- **`squeeze` = the anamorphic factor** (2.0 = a 2x squeeze, the classic anamorphic). Only the
  horizontal axis is scaled; vertical passes through.
- **Tag the output Raw/Data** and STMap it onto the squeezed plate.
- Reframe/refit after, since the unsqueeze changes the working width.
