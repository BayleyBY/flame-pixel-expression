# heat_haze_map

**What it does:** fbm-driven UV-offset ST map; `amp` strength, keyframe `seed` to shimmer.

**Use case:** Heat-haze / refraction wobble — feed an STMap node.

**Inputs:** none (generator → STMap)

**Expects:** any input; outputs an ST/UV map — tag output Raw/Data

**Variables:** `scale` (120.0), `seed` (0.0), `lacunarity` (2.0), `persistence` (0.5), `amp` (0.03)

## Notes

A **heat-haze / refraction ST map** — `red = U, green = V` feeding a downstream **STMap node**
(this node → STMap **map/UV input**, plate → STMap **source input**). Output tagged **Raw/Data**.

### What it does
Offsets each pixel's source UV by an **animated 3-octave fbm** field (the shared `_FBM_NOISE`
builder) times **`amp`**. X and Y use the same noise field sampled at different offsets, so they
wobble independently — the organic shimmer of hot air or water refraction.

### Controls
- **`seed`** — **keyframe this to animate the shimmer** (the node has no time variable; the seed
  offset into the noise field is how you get motion).
- **`amp`** = displacement strength (UV units; 0.03 default ≈ a few percent of the frame).
- **`scale`** = feature size, **`lacunarity`**/**`persistence`** shape the fbm octaves.
