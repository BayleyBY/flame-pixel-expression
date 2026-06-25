# false_color_exposure

**What it does:** ARRI/RED-style exposure false-colour: luma → stops from 18% grey (`s = log2(L/0.18)+exposure`), banded into purple/blue/teal/green/yellow/orange/red.

**Use case:** Judge exposure at a glance — find clipped blacks/whites and the 18% midtone band.

**Inputs:** Front 1

**Expects:** scene-linear (the 18% grey reference and log2 stop bands assume scene-linear luma)

**Variables:** `exposure` (0.0)

## Notes

A **monitoring false-colour**, like the one on an ARRI/RED/Sony viewfinder: it recolours the
image by exposure so you can *see* where the stops land instead of guessing.

### The bands
Luminance is converted to **stops from 18% grey** (`s = log2(L/0.18) + exposure`) and quantised:

| Colour | Meaning |
|--------|---------|
| Purple | deep shadow / near clip-black (`s < -4`) |
| Blue → teal | low values (`-4 … -0.5`) |
| **Green** | the 18% midtone band (`-0.5 … 0.5`) — expose skin/key here |
| Yellow → orange | highlights (`0.5 … 4`) |
| Red | near clip-white (`s > 4`) |

### Use it
- Drop on a monitor branch, judge exposure, then **bypass** it for the real grade.
- `exposure` slides every band together (preview a stop up/down).
- **Expects scene-linear** — the 18% reference and the `log2` stops assume linear light. On
  log/display footage the bands won't line up with real stops.
