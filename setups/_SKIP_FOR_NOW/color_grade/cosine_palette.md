# cosine_palette

**What it does:** Maps Front 1 luminance through an IQ cosine palette (`col = a + b*cos(2π*(c·t+d))`, a/b/c/d baked rainbow). `tScale`/`tOffset` shape the driver.

**Use case:** Heatmap/thermal LUT/false-colour a depth, mask or scalar pass; stylised one-knob regrade.

**Inputs:** Front 1 (any scalar — wire depth/pattern here)

**Expects:** any — the driver is a luma dot-product, so feed it whatever scalar you want mapped (depth, mask, value)

**Variables:** `tScale` (1.0), `tOffset` (0.0)

## Notes

A **scalar → colour mapper** built on Inigo Quilez's cosine-palette formula
`col = a + b·cos(2π·(c·t + d))`. It turns any single value into a smooth, rich gradient —
the cheapest way to make a depth pass, a mask, or a noise field *readable* as colour.

### How it works
- The driver `t` = Rec.709 luminance of Front 1, shaped by `tScale` (contrast) and `tOffset`
  (slide the ramp). So **whatever you wire to Front 1 gets mapped by its brightness** — an
  image, a depth pass, an SDF, one of the `noise/` generators.
- `a, b, c, d` are baked as **literals** (the classic rainbow: a=b=0.5, c=1, d=0/⅓/⅔) so they
  cost zero variable slots. Edit them in the generator if you want a different palette
  (warm/teal, thermal, two-tone).

### Recipes
| Want | Move |
|------|------|
| Thermal/heatmap of depth | wire depth (on Front 1), raise `tScale` to spread the band |
| Slow the rainbow | lower `tScale` (e.g. 0.5) |
| Shift which value is red | `tOffset` |

Pair with `false_color_exposure` (discrete bands) when you need *readable stops* rather than a
continuous ramp.
