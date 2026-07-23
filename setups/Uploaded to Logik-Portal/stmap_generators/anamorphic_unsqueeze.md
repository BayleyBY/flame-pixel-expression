# anamorphic_unsqueeze

**What it does:** Horizontal stretch ST map; `squeeze` = anamorphic factor (2.0 = 2x).

**Use case:** Unsqueeze anamorphic footage to its correct aspect.

**Inputs:** none (generator → STMap)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

**Variables:** `squeeze` (2.0)

## Node dependencies
**Pipeline:** **this node** → **STMap**

Outputs a 0..1 **ST/UV map** (`red`=U, `green`=V) — *coordinates*, not a warped image. On its own it looks like a red/green gradient and changes nothing. Wire its output into a downstream **STMap** node's map/UV input, and the plate you want warped into the STMap's source — the STMap does the re-sample (the pixel gather this node can't do). **Tag the map Raw/Data**; colour-managing a coordinate map corrupts the warp. Horizontal unsqueeze (e.g. `squeeze` 2.0 for 2x anamorphic).

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

A horizontal-stretch **ST map** to un-squeeze anamorphic footage back to its true aspect.
Outputs `red = U, green = V`; feed it to an STMap node.

### Practical notes
- **`squeeze` = the anamorphic factor** (2.0 = a 2x squeeze, the classic anamorphic). Only the
  horizontal axis is scaled; vertical passes through.
- **Tag the output Raw/Data** and STMap it onto the squeezed plate.
- Reframe/refit after, since the unsqueeze changes the working width.
