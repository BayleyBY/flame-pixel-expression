# depth_dof_mask

**What it does:** 0 at the `focus` plane, ramping to 1 over `range`.

**Use case:** Drive a Defocus node's blur amount for depth of field.

**Inputs:** Matte 1 = depth

**Expects:** raw / data (no colour management)

**Variables:** `focus` (0.5), `range` (0.2)

## Node dependencies
**Pipeline:** depth pass (Matte 1) → **this node** → variable-blur / Defocus

Emits a per-pixel **blur amount** (0..1), not a blurred image — the node can't gather neighbours. Feed it into a downstream **variable-blur / Defocus** node as its blur-amount (matte) input, with the plate on that node's front. Output is data — tag it Raw/Data. A 0..1 in-focus/out-of-focus **mask** from the depth pass on Matte 1 — art-directed falloff rather than a physical CoC.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Builds a **blur-amount mask** for depth of field: 0 at the `focus` plane, ramping to 1 as
depth departs focus in either direction. It does *not* blur — it drives a blur.

### How to wire it
Feed the **output into the blur-amount / defocus input of a Defocus node**, not into an
image input. The node reads this mask per pixel to decide how much to defocus there.

### Practical notes
- **Depth on Matte 1.** `focus` = the depth that stays sharp; `range` = how quickly things
  defocus away from it (smaller = shallower DOF).
- Symmetric — objects nearer *and* farther than focus both blur, as a real lens does.
- Keyframe `focus` for a rack-focus pull.

### Quick test
Fake depth: `radial_ramp` output into **Matte 1** → **a black band (in focus) where the
ramp crosses `focus` 0.5, white elsewhere**; slide `focus` 0→1 and the band sweeps across
frame. Remember it outputs a blur-AMOUNT mask for a downstream variable-blur/Defocus — it
never blurs by itself.
