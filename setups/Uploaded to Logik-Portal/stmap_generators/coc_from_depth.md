# coc_from_depth

**What it does:** Per-pixel circle-of-confusion radius (0..1) from depth on Matte 1; `focusDepth/Range`, `maxBlur`.

**Use case:** Drive a variable-blur/Defocus node's blur-amount map for depth-of-field.

**Inputs:** Matte 1 (depth)

**Expects:** depth raw in; outputs a 0..1 blur-amount map (Raw/Data)

**Variables:** `focusDepth` (5.0), `focusRange` (5.0), `maxBlur` (1.0)

## Node dependencies
**Pipeline:** depth pass (Matte 1) → **this node** → variable-blur / Defocus

Emits a per-pixel **blur amount** (0..1), not a blurred image — the node can't gather neighbours. Feed it into a downstream **variable-blur / Defocus** node as its blur-amount (matte) input, with the plate on that node's front. Output is data — tag it Raw/Data. It reads the **depth pass on Matte 1** and outputs a circle-of-confusion radius from `focusDepth` / `focusRange` / `maxBlur` — so it needs depth *in* and a defocus node *out*. Set `focusDepth` to your focal plane's depth value.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

**NOT a UV map** — this outputs a **per-pixel circle-of-confusion (blur-amount) map**, written
to RGB **and** the Matte. Depth arrives on **Matte 1 (`m1`)** per the library convention.

### Required downstream wiring
Feed this into a **variable-blur / Defocus / depth-of-field node** as its **blur-amount input**
(the map that says how much to blur each pixel). The blur node does the gathering — this node
only computes the amount (no neighbour sampling is possible here).

### What it does
`coc = clamp(abs(m1 - focusDepth) / focusRange, 0, 1) * maxBlur`. Pixels at `focusDepth` get 0
(sharp); blur ramps up with distance from the focus plane, reaching `maxBlur` at the edge of
`focusRange`.

### Controls
- **`focusDepth`** = the depth value held in focus (match your depth pass's units/scale).
- **`focusRange`** = how far from focus before reaching max blur.
- **`maxBlur`** = output scale (0..1) — set so it matches your blur node's expected amount range.
- Tag the output **Raw/Data** (it's a control map, not an image).
