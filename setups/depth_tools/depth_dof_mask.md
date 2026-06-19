# depth_dof_mask

**What it does:** 0 at the `focus` plane, ramping to 1 over `range`.

**Use case:** Drive a Defocus node's blur amount for depth of field.

**Inputs:** Matte 1 = depth

**Expects:** raw / data (no colour management)

**Variables:** `focus` (0.5), `range` (0.2)

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
