# rgb_to_hsv

**What it does:** Converts RGB to HSV (H,S,V on R,G,B).

**Use case:** Inspect or feed hue/sat/value into other tools.

**Inputs:** Front 1

**Expects:** any (operates on the RGB values as given)

_No variables._

## Node dependencies
**Pipeline:** **this node** → an HSV consumer (e.g. `hsv_to_rgb`)

Emits an **HSV-encoded** image (H,S,V in R,G,B) — not a display picture. Bracket a hand-built HSV operation with `rgb_to_hsv` … `hsv_to_rgb`, or feed any node that expects HSV.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Converts RGB → **HSV**, packing **H on red, S on green, V on blue** (branchless Hocevar
conversion). The foundation of the `hsv_color/` folder.

### How to use it
Decode here, manipulate the H/S/V channels with any value op, then `hsv_to_rgb` to reconstruct
— the round-trip that makes hue/sat/value individually addressable. H is 0..1 and **wraps**
(0 and 1 are the same red).

### Practical notes
- The node does **no colour management** — it operates on the values as given; results depend
  on the space your pixels are in.
- Most tools here (`chroma_key`, `vibrance`, `sat_matte`…) reuse this same decode internally,
  so you rarely need it explicitly unless you want to view or hand-edit the channels.
