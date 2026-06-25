# matte_falloff_ramp

**What it does:** Feathers a matte by remapping its own values — `smoothstep(lo, hi, m1)` shaped by `gamma`. NOT a blur (no gather): reshapes existing soft coverage only.

**Use case:** Tighten/spread an existing soft edge, or gamma a matte's falloff, without a blur node.

**Inputs:** Matte 1

**Expects:** any (data / value op)

**Variables:** `lo` (0.0), `hi` (1.0), `gamma` (1.0)

## Notes

Feathers a matte by **remapping its own coverage values** — `smoothstep(lo, hi, m1)` shaped by
`gamma`. Pull `lo`/`hi` together to harden the edge, apart to spread it; `gamma` biases the
falloff.

### The honest limit
This is **not a blur** — the node can't gather neighbours, so it cannot create edge width where
none exists. It can only *reshape* the soft transition a matte already has (an anti-aliased or
keyed edge). For a true grow/shrink/blur, use a real blur node downstream. Result on RGB + Matte.
