# vibrance

**What it does:** Smart saturation — `vibrance` lifts low-sat pixels more than vivid ones, `saturation` is a master scale, `skinProtect` spares skin hues.

**Use case:** Add punch without clipping already-saturated colours or wrecking skin.

**Inputs:** Front 1

**Expects:** your working/display space (saturation-based)

**Variables:** `vibrance` (0.0), `saturation` (1.0), `skinProtect` (0.0)

## Notes

A **smarter saturation** than a flat multiply. A plain saturation control pushes every
pixel equally, so the colours that were already vivid clip and posterize first while the
muted ones still look flat. `vibrance` measures each pixel's current saturation and lifts
the *low*-saturation pixels more than the already-vivid ones — you get punch in the dull
areas without blowing out the colours that were fine.

### How it works
The boost factor is `1 + vibrance * (1 - S)`, where `S` is the pixel's HSV saturation. So
a grey-ish pixel (`S` near 0) gets the full lift, a saturated pixel (`S` near 1) is barely
touched. That result is then scaled by a master `saturation`, and the whole move is faded
out near skin hues by `skinProtect`. Every channel is `mix(luma, original, factor)`, so
brightness is held fixed — only chroma moves.

### Controls
- `vibrance` — the smart lift (0 = off). Positive adds, negative pulls dull colours toward
  grey while sparing vivid ones.
- `saturation` — a plain master multiply on top (1.0 = unchanged), if you also want a
  flat push.
- `skinProtect` — 0..1, how strongly to spare the skin-hue band (~orange) so faces don't go
  radioactive when you push everything else.

### Why use it
The classic problem: a shot needs more life, but cranking saturation makes the red jacket
or the green sign clip and band before the rest catches up. Vibrance fills in the muted
mid-saturation colours and leaves the already-saturated ones alone — the standard
"give it some pop without it looking cartoonish" move.

### Practical notes
- **Lead with `vibrance`, not `saturation`** for natural results; reach for `saturation`
  only when you genuinely want an even push across the whole frame.
- **Turn on `skinProtect`** whenever there are people in frame and you're pushing hard.
- Negative `vibrance` is a gentle, vivid-preserving **de**-saturation — handy for calming a
  busy background without flattening its few strong colours.
