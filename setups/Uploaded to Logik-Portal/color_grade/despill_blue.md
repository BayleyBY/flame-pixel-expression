# despill_blue

**What it does:** Reduces blue where it exceeds the red/green average; `spill` 0→1 sets strength.

**Use case:** Remove blue-screen spill from a foreground.

**Inputs:** Front 1

**Expects:** your working space (keep consistent)

**Variables:** `spill` (1.0)

## Notes

**Blue-screen despill** — clamps the blue channel to no more than the average of red and
green (`min(b, (r+g)/2)`), the standard suppression. `spill` blends from 0 (off) to 1 (full).

### Practical notes
- Removes blue contamination on edges and transmissive areas before/after keying; red and
  green pass through untouched.
- For a **green** screen use `despill_green` instead.
