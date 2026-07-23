# crosshatch

**What it does:** Pen crosshatch: 0/45/90/135-degree line sets switch on as luma darkens through four thresholds (darker = more hatch directions).

**Use case:** Ink-illustration / engraving look, sketch stylisation, comic shading.

**Inputs:** Front 1

**Expects:** display-referred / working image (luma-driven look)

**Variables:** `spacing` (8), `lineW` (0.5), `aR` (0.0), `aG` (0.0), `aB` (0.0), `bR` (1.0), `bG` (1.0), `bB` (1.0)

## Notes

**Pen-and-ink crosshatch shading.** As a region darkens it accumulates more sets of
parallel lines — first one direction, then a second crossing it, then a third and fourth —
exactly how an illustrator builds up tone with a pen. The result is ink-on-paper line art
driven entirely by the image's luminance.

### How it works
Four line fields at **0, 45, 90 and 135 degrees** are generated with `sin` of the
(rotated) coordinates. Each field is gated by a luma threshold: lines at 0 deg appear once
luma drops below 0.8, the 45-deg set joins below 0.6, 90 deg below 0.4, 135 deg below 0.2.
The lit fields are multiplied together (a line in *any* active direction = ink), so darker
pixels are crossed by progressively more hatching.

### Controls
- `spacing` — pixels between hatch lines. Smaller = finer, denser pen.
- `lineW` — 0..1 line weight / softness (how fat each stroke is relative to the gap).
- `aR..bB` — ink and paper colours (default black ink on white paper).

### Notes
- Expects a **display-referred / working image** — the four thresholds (0.8/0.6/0.4/0.2)
  assume a roughly 0..1 display range. If your image is linear or log, run an exposure /
  view transform first so the tones land where the thresholds expect them.
- Great over a high-contrast, slightly blurred version of the plate — fine detail otherwise
  fights the hatch lines.
