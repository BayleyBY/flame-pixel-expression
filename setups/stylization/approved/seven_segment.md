# seven_segment

**What it does:** Burns one SDF 7-segment digit (value `digit` 0..9) into the frame at Centre — no text node. Keyframe `digit` for a frame counter.

**Use case:** On-screen counters/timers/HUD numerals, retro display overlays, datamosh captions.

**Inputs:** none (generator; composite over your plate)

**Expects:** any — generates data/values

**Variables:** `digit` (0.0), `digScale` (150), `thick` (0.1), `hw` (0.42), `hh` (0.42), `lit` (1.0)

## Notes

A **single 7-segment digit** rasterised straight into the frame from a number — no Text
node, no font, no external matte. The seven bars are signed-distance boxes laid out in the
classic calculator/LED arrangement, and which ones light is decided by an **arithmetic
truth table** on the `digit` variable (0..9). Keyframe `digit` and you have a **frame
counter / timer** baked into the comp.

### How it works
Local coordinates are taken relative to **Centre** and normalised by `digScale`. For each of
the seven segments (a=top ... g=middle) a per-digit selector — built from `step()` equality
tests against `floor(digit + 0.5)` — multiplies that bar's box fill, and the seven results
are `max`-combined into the lit shape `seg`. No loop, no array: the truth table is unrolled
into the expression.

### Controls
- `digit` — 0..9. **Keyframe it** (e.g. 0->9 over 10 frames, repeating) to count. Values are
  rounded, so a linear keyframe steps cleanly through the digits.
- `digScale` — pixel half-height of the digit.
- `thick` — stroke half-width (segment fatness) in local units.
- `hw` / `hh` — half-length of the horizontal / vertical bars (tune the proportions).
- `lit` — brightness of the lit segments (the unlit/background tone is near-black with a
  faint green tint for an LED feel).

### Recipes
- **Frame counter:** keyframe `digit` 0->9 linearly across 10 frames, set the channel to
  cycle/repeat. Place several copies at different Centres for multi-digit readouts.
- **Countdown leader:** keyframe `digit` 9->0 over your countdown and composite over the
  plate.

### Notes
- A **generator** — composite the result over your plate (the matte gives you the digit
  shape for the merge).
- It's **one digit by design**; for a multi-digit display, duplicate the node and offset
  each Centre, driving each `digit` from the appropriate place value.
