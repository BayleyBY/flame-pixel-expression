# zone_system_posterize

**What it does:** Quantises luma into `zones` greyscale steps (Ansel Adams zone system) spanning 0..1. matte = the zone value.

**Use case:** Read the exposure distribution as discrete zones; also a clean posterized look.

**Inputs:** Front 1

**Expects:** scene-linear (Rec.709 luma); the zones read as exposure steps

**Variables:** `zones` (11.0)

## Notes

Quantises luminance into `zones` discrete greyscale steps spanning 0..1 — Ansel Adams' **zone
system** as a live readout. Flat bands make the exposure *distribution* obvious (where the image
sits across the tonal range), and it doubles as a clean posterized look. `matte` carries the zone
value. Default `zones` = 11 (Zones 0–X). **Expects scene-linear** so the steps read as exposure
zones; feed display-referred and they're just tonal bands.
