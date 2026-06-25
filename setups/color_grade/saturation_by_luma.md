# saturation_by_luma

**What it does:** Saturation that varies with luma: ramps from `satLow` (shadows) to `satHigh` (highlights) across [`loThr`..`hiThr`], mixing each channel toward grey.

**Use case:** Desaturate only shadows (or only highlights) — tame noisy blacks or electric speculars without a global pull.

**Inputs:** Front 1

**Expects:** scene-linear (Rec.709 luma weights)

**Variables:** `satLow` (1.0), `satHigh` (1.0), `loThr` (0.2), `hiThr` (0.8)

## Notes

Saturation that **depends on brightness** — the single most common "advanced" saturation move.
Instead of one global pull, the amount ramps from `satLow` (in shadows) to `satHigh` (in
highlights) across luma `loThr`..`hiThr`, then each channel mixes toward grey (`L`) by that amount.

### Recipes
| Goal | Move |
|------|------|
| Kill noisy chroma in the blacks | `satLow` ~0.3, leave `satHigh` 1.0 |
| Tame electric highlights | `satHigh` ~0.5 (or use `highlight_desaturate`) |
| Boost only midtones | raise both thresholds inward, `satLow`/`satHigh` 1.0, mid >1 |

Defaults (`satLow`=`satHigh`=1.0) are identity. **Expects scene-linear** (Rec.709 luma weights).
