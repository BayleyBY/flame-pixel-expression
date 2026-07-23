# hue_preserving_clip

**What it does:** Clamps to `ceiling` by scaling all three channels by the same factor (`ceiling/max`), so hue is preserved — unlike per-channel clip (which twists hue) or `gamut_clip` (which only flags).

**Use case:** Bring over-range pixels back in range for a display/delivery clamp without hue shifts.

**Inputs:** Front 1

**Expects:** any (display- or scene-referred; rescales raw channel values to `ceiling`)

**Variables:** `ceiling` (1.0)

## Notes

Clamps over-range pixels to `ceiling` by **scaling all three channels by the same factor**
(`ceiling / max(r,g,b)`), so the **hue and saturation ratio are preserved**. A naïve per-channel
`min(x, 1)` clips each channel independently and **twists the hue** of bright saturated colours
(e.g. an orange clips toward yellow). This avoids that.

### vs `gamut_clip`
`gamut_clip` is a **QC** tool — it *flags* illegal pixels with warning tints and changes nothing
else. `hue_preserving_clip` is a **fix** — it *rescales* the pixel back into range. Use
`gamut_clip` to find problems, this to resolve them for a display/delivery clamp.
