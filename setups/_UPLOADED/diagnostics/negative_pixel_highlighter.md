# negative_pixel_highlighter

**What it does:** Flags pixels with any channel below −`eps` in green (`tint` = opacity); valid pixels pass through. matte = the negative mask.

**Use case:** Spot negative light (filter ringing, bad comps) before it breaks log/math — `aov_clamp_negative` fixes; this finds.

**Inputs:** Front 1

**Expects:** scene-linear / your working space (negative-channel detection on raw values)

**Variables:** `eps` (0.0), `tint` (1.0)

## Notes

**Finds** pixels with any channel below −`eps` and marks them green (`tint` = opacity); everything
valid passes through, and `matte` carries the negative mask. Negative light comes from filter
ringing, bad un-premults, or over-shooting grades, and it silently breaks later log/exp math.

### vs `aov_clamp_negative`
`aov_clamp_negative` **fixes** negatives (clamps them to 0). This one **flags** them so you can see
*where* they are before deciding how to treat them. Use this to diagnose, that to repair.
