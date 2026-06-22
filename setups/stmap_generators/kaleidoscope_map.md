# kaleidoscope_map

**What it does:** Mirror-folds angular space into `segments` wedges around Centre; `rot` spins it.

**Use case:** Kaleidoscope / mirror-symmetry looks — feed an STMap node.

**Inputs:** none (generator → STMap)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

**Variables:** `segments` (6.0), `rot` (0.0)

## Notes

A **kaleidoscope ST map** — `red = U, green = V` feeding a downstream **STMap node** (this node
into the STMap's **map/UV input**, the plate into its **source input**). Output tagged
**Raw/Data**.

### What it does
Mirror-folds angular space into **`segments`** wedges around the node **Centre**, then
reconstructs a source UV from the folded angle + original radius. The STMap then samples your
plate through that folded coordinate field, giving the mirror-symmetry kaleidoscope look.

### Controls
- **`segments`** = number of mirrored wedges (6 default).
- **`rot`** = rotation of the fold (radians) — spin it for an animated kaleidoscope.
- Drag **Centre** to move the pivot. Keyframe `rot` for motion.
