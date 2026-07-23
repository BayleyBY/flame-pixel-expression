# aov_clamp_negative

**What it does:** Clamps sub-zero pixels to 0 per channel.

**Use case:** Clean negative values some renderers emit before further math.

**Inputs:** Front 1

**Expects:** any (data / value op)

_No variables._

## Notes

Floors every channel at 0 — strips the **sub-zero values** renderers sometimes emit
(negative lobes from filtering/sharpening, stray specular, OpenEXR round-trips).

### Why it matters
Tiny negatives are invisible until an operation chokes on them: `pow`/log encodes go NaN,
`screen_merge` and other multiplicative comps misbehave, glows pick up dark fringes. This is
a cheap **safety pass** to drop in before any of those.

### Practical notes
- No controls — `max(channel, 0)` per channel; keeps alpha (`matte = m1`).
- Put it **before** `screen_merge`, a log/sRGB encode, or a glow extraction.
