# highlight_desaturate

**What it does:** Collapses chroma toward the max channel above `thr` (feathered over `soft`, scaled by `amount`) — pulls bright colours toward white.

**Use case:** Fix over-saturated CG speculars, neon clipped skies, and electric highlights.

**Inputs:** Front 1

**Expects:** scene-linear (operates on the max channel / highlights)

**Variables:** `thr` (1.0), `soft` (1.0), `amount` (1.0)

## Notes

Pulls **bright, over-saturated colour toward white**. Above `thr` (feathered over `soft`) each
channel is mixed toward the pixel's max channel by `amount` — so a clipped neon-blue sky or an
electric CG specular rolls off to a believable white-hot instead of a saturated blob.

Distinct from `saturation_by_luma`: that scales chroma by luma generally; this specifically
collapses chroma toward white in the highlights. **Expects scene-linear.**
