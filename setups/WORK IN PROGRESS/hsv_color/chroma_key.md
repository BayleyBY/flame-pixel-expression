# chroma_key

**What it does:** Matte from hue distance to `keyHue` with a `satMin` floor.

**Use case:** Quick chroma key by colour (greens, blues, skin).

**Inputs:** Front 1

**Expects:** your working/display space (hue-based)

**Variables:** `keyHue` (0.33), `tol` (0.05), `soft` (0.05), `satMin` (0.15)

## Notes

The **hue qualifier**: a matte that's white where a pixel's hue is near `keyHue` and its
saturation clears `satMin`, black elsewhere. Written to RGB **and** the Matte.

### Controls
- `keyHue` = target hue (0..1: red 0.0, green 0.33, blue 0.66…); `tol` = band half-width;
  `soft` = edge feather; `satMin` = saturation floor that **rejects greys** (whose hue is
  meaningless/unstable).

### Practical notes
- Quick key by colour (greens, skies, skin). Its saturation-axis sibling is `sat_matte`;
  `matte_and` the two for a tighter "this hue *and* this vividness" selection.

### Quick test
Point it at something **green** (defaults key green): matte goes white on the green, black
elsewhere — on RGB (view Result) and on OutMatte (only once **Matte 1 is wired**). A frame
with nothing green/saturated is correctly ALL BLACK: sample your target and set `keyHue`
(0 = red, ⅓ = green, ⅔ = blue; red wraps safely), then widen `tol` until the matte fills.
