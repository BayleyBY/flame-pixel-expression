# srgb_to_linear

**What it does:** Exact piecewise sRGB → linear decode.

**Use case:** Linearise sRGB-encoded footage before doing light-linear math.

**Inputs:** Front 1

**Expects:** sRGB-encoded 0–1 in → linear out

_No variables._

## Node dependencies
**Pipeline:** display-encoded sRGB → **this node** → linear-only ops → `linear_to_srgb`

Decode half of an **encode/decode pair**: bracket linear-domain maths (exposure, merges, light math) between this and **`linear_to_srgb`**. A convenience when a proper OCIO/colour-management node isn't available — not a replacement for your colour pipeline.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Exact piecewise **sRGB → linear decode**. The node does no colour management itself, so this
is the manual "linearise before light math" step.

### When you need it
All the physically-meaningful operations in this library — `exposure`, `white_balance`,
`aov_*` light-pass math, `normal_relight`, fog/depth blends — assume **scene-linear** input.
If your footage is sRGB-encoded (most 8-bit/display sources), decode it first or those ops
will give wrong results (crushed shadows, off colours).

### Practical notes
- **Pair it with `linear_to_srgb`**: decode → do your linear work → re-encode for
  display/output. They're exact inverses, so a decode/encode round-trip with nothing between
  is a no-op.
- This is the *exact* piecewise sRGB curve (linear toe + 2.4 gamma segment), not the 2.2
  approximation — match it on the encode side.
- Only for sRGB-encoded sources. Don't run it on data passes (P, normals, depth, ST maps,
  Cryptomatte) — those are already linear/raw and must stay untouched.

### Quick test
Mids and shadows visibly **darken**: a 0.5 grey pixel must come out **0.214** (read it with
the colour picker). Round-trip check: chain `linear_to_srgb` after it → output equals the
input exactly (verify with `difference_matte`, gain cranked — solid black).
