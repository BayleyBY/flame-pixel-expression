# linear_to_srgb

**What it does:** Exact piecewise linear → sRGB encode.

**Use case:** Re-encode to sRGB for display/output after linear work.

**Inputs:** Front 1

**Expects:** linear in → sRGB-encoded out

_No variables._

## Node dependencies
**Pipeline:** `srgb_to_linear` (or scene-linear source) → linear-only ops → **this node**

Encode half of the pair: re-applies the sRGB curve after working in linear. Keep it matched with **`srgb_to_linear`** so the round-trip is lossless; prefer real colour management when you have it.

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Exact piecewise **linear → sRGB encode** — the re-encode half of the pair. Run it *after*
your linear work to put pixels back into a display-referred sRGB space for viewing or output.

### Practical notes
- **Pair with `srgb_to_linear`**: decode → linear ops → encode. The two are exact inverses,
  so the round-trip is lossless when nothing happens in between.
- Encode as the **last** step — anything after it (more grades, light math) would be
  operating on display-encoded values and misbehave.
- Exact piecewise sRGB, not a 2.2 gamma approximation; use the matching decode upstream.
- Data passes (P, normals, depth, ST maps, crypto) are linear/raw by definition — never
  sRGB-encode them.
