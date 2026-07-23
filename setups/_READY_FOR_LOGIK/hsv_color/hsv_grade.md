# hsv_grade

**What it does:** Grades HSV-ENCODED data: wrapping `hueShift`, sat gain + gamma, value gain + gamma.

**Use case:** Edit hue/sat/value directly between `rgb_to_hsv` and `hsv_to_rgb` — sat gamma has no RGB-space equivalent.

**Inputs:** Front 1 = HSV (from `rgb_to_hsv`)

**Expects:** HSV data in → HSV data out (bracket with `rgb_to_hsv` … `hsv_to_rgb`)

**Variables:** `hueShift` (0), `satGain` (1.0), `satGamma` (1.0), `valGain` (1.0), `valGamma` (1.0)

## Node dependencies
**Pipeline:** `rgb_to_hsv` → **this node** → `hsv_to_rgb`

Operates on an **HSV-encoded** image (H,S,V in R,G,B) — it is the middle of the decode → modify → encode sandwich and produces HSV data, not a picture. Both bracket nodes are required.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

**A grade that runs INSIDE the HSV sandwich** — this node expects **HSV-encoded** data
(H on red, S on green, V on blue, i.e. the output of `rgb_to_hsv`), not a picture. It exists
to demonstrate what becomes trivial once hue/sat/value are ordinary channels:

- `hueShift` — **additive hue rotation that wraps for free** (`fract`, matching the decoder):
  0.5 flips every colour to its complement, small values nudge a cast around the wheel.
- `satGain` × `satGamma` — gain scales saturation; **gamma contours it**: `satGamma` > 1
  drains weakly-coloured pixels to grey while fully-saturated ones keep their punch
  (a per-pixel "saturation soft-knee" with no RGB-space equivalent — `vibrance` is the
  closest single-node cousin).
- `valGain` × `valGamma` — a brightness gain + gamma applied to V only, so hue and
  saturation are mathematically untouched (unlike an RGB gamma, which shifts saturation).

Neutral defaults (`hueShift` 0 / gains and gammas 1) make it a pass-through.

### Practical notes
- S is clamped to 0..1 on output — over-range saturation would make `hsv_to_rgb`
  extrapolate to negative RGB. V is deliberately NOT clamped (over-range highlights
  survive the round-trip); add `hue_preserving_clip` after the sandwich for delivery.
- Viewed directly (without `hsv_to_rgb` downstream) the output looks like false-colour
  data — that's correct.
- For a one-node version of the common cases, the dedicated `hsv_color/` tools
  (`hue_rotate`, `vibrance`, `hsl_targeted`…) do their own decode internally; reach for
  the sandwich when you want ops they don't offer, or several HSV edits paying the
  decode cost once.

### Quick test
Wire a colourful clip → `rgb_to_hsv` → **this node** → `hsv_to_rgb` (Front 1 each time).
With the defaults the chain output matches the source exactly (pass-through). Set
`hueShift` 0.5 → **every colour flips to its complement** (reds↔cyans, greens↔magentas).
Back to 0, set `satGamma` 3.0 → **pale/washed areas drain to grey while strongly-coloured
areas keep their punch**. Viewing this node's own output (no `hsv_to_rgb`) shows
false-colour HSV data — that's correct, not a bug.
