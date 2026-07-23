# glitch_block_map

**What it does:** Block-shuffle ST map; hashes `blockSize` blocks and offsets them by `corruption`.

**Use case:** Datamosh / block-glitch — keyframe `corruption` to trigger, feed an STMap node.

**Inputs:** none (generator → STMap)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

**Variables:** `blockSize` (64.0), `corruption` (0.0), `seed` (0.0)

## Node dependencies
**Pipeline:** **this node** → **STMap**

Outputs a 0..1 **ST/UV map** (`red`=U, `green`=V) — *coordinates*, not a warped image. On its own it looks like a red/green gradient and changes nothing. Wire its output into a downstream **STMap** node's map/UV input, and the plate you want warped into the STMap's source — the STMap does the re-sample (the pixel gather this node can't do). **Tag the map Raw/Data**; colour-managing a coordinate map corrupts the warp. Block-shuffle / datamosh — **keyframe `corruption`** (0→1) to trigger; `seed` reshuffles the blocks.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

A **block-shuffle / datamosh ST map** — `red = U, green = V` feeding a downstream **STMap node**
(this node → STMap **map/UV input**, plate → STMap **source input**). Output tagged **Raw/Data**.

### What it does
Quantises the frame into **`blockSize`-pixel blocks**, hashes each block's index to a random
2D offset (via the shared `_hash2` helper), and shifts that whole block's source UV by the hash
scaled by **`corruption`**. Each block jumps as a unit, so the STMap tears the plate into
displaced rectangles — a corrupted-codec / datamosh look.

### Controls
- **`corruption`** 0..1 — the trigger. **Keyframe it** (e.g. 0 → 0.8 → 0 over a few frames) so
  the glitch pops in and out; at 0 the map is identity (no displacement).
- **`blockSize`** = block size in pixels (smaller = finer shredding).
- **`seed`** reshuffles which way each block jumps — keyframe it to re-randomise per frame.
