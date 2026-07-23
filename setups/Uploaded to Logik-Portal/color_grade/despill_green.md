# despill_green

**What it does:** Reduces green where it exceeds the red/blue average; `spill` 0→1 sets strength.

**Use case:** Remove green-screen spill from a foreground.

**Inputs:** Front 1

**Expects:** your working space (keep consistent)

**Variables:** `spill` (1.0)

## Notes

**Green-screen despill** — clamps the green channel to no more than the average of red and
blue (`min(g, (r+b)/2)`), the standard suppression. `spill` blends from 0 (off) to 1 (full).

### Practical notes
- Removes green contamination on edges and transmissive areas before/after keying; red and
  blue pass through untouched.
- For a **blue** screen you'd suppress blue instead — that's a separate generated variant
  (edit `generate_setups.py`, don't hand-edit the file).
