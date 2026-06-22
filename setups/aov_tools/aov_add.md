# aov_add

**What it does:** Sums two passes with per-pass gain.

**Use case:** Beauty rebuild — add diffuse+specular etc.; chain nodes for more passes.

**Inputs:** Front 1 + Front 2

**Expects:** scene-linear

**Variables:** `gainA` (1.0), `gainB` (1.0)

## Node dependencies
**Pipeline:** pass A (Front 1) + pass B (Front 2) → **this node**

Consumes specific **render AOVs/passes** delivered by your renderer or extracted from EXR layers upstream (a Read/MUX/Channel node). The passes are data/light — keep them in the right space (linear for light math) and wire each to the input named below. Recombine light AOVs by addition (work in scene-linear).

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Sums two light/AOV passes with a per-pass gain — `pass1 * gainA + pass2 * gainB`. The atom
of **render-pass recombination**: in linear, a beauty *is* the sum of its light components
(diffuse + specular + GI + …).

### The chaining workflow
The node only has two RGB inputs, so to rebuild a full beauty from many passes you **chain**:
this node's Result becomes the next node's Front 1 (a running sum), Front 2 is the next pass.

### Practical notes
- **Must be scene-linear** — additive pass math is only correct on linear light.
- `gainA`/`gainB` let you **rebalance** as you recombine: kill the specular, push the GI,
  etc., without re-rendering.
- Keeps Front 1's alpha (`matte = m1`).
