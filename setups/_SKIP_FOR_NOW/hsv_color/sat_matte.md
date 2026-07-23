# sat_matte

**What it does:** Matte from a saturation window [`satLow`,`satHigh`] gated by a `valMin` brightness floor.

**Use case:** Qualifier that isolates vivid vs neutral regions to drive a downstream grade.

**Inputs:** Front 1

**Expects:** your working/display space (saturation-based)

**Variables:** `satLow` (0.15), `satHigh` (1.0), `soft` (0.05), `valMin` (0.0)

## Notes

A **qualifier**, not a grade: it outputs a matte that is white where a pixel's saturation
falls inside a window and black elsewhere, so you can isolate *vivid* vs *neutral* regions
and drive a downstream correction with the result. It's the saturation-axis sibling of
`chroma_key` (which qualifies by hue).

### How it works
The matte is `inside(S, satLow..satHigh)` with soft edges, multiplied by a `valMin`
brightness floor so dark, noisy, near-black pixels don't sneak in. The result is written to
RGB **and** the Matte field, so you can use Result or OutMatte downstream.

### Controls
- `satLow` / `satHigh` — the saturation window to keep (default `0.15..1.0` = "anything
  reasonably colourful").
- `soft` — feathers both edges of the window so the matte isn't binary.
- `valMin` — brightness floor; raise it to reject dark regions whose hue/sat is unreliable.

### Why use it
Lots of fixes want "only the colourful bits" or "only the greys": pull a mask of the
saturated product on a neutral set, protect already-vivid areas from a global saturation
push, find blown-out neon to tame, or isolate the desaturated background to grade
separately. Because it's saturation-based it catches colour the way a hue key can't — it
doesn't care *which* colour, only *how* colourful.

### Practical notes
- **Invert it** (feed through `matte_invert`, or swap the window) to select the *neutral*
  regions instead of the vivid ones.
- **Combine with hue** — chain after `chroma_key` via `matte_and` to get "this hue *and*
  this saturation", a much tighter selection than either alone.
- Raise `valMin` first if a noisy shadow area is leaking into the matte.
