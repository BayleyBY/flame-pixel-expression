# voxelize

**What it does:** Quantises colour to `scale` steps per channel.

**Use case:** Posterise/banding look, colour reduction, stylise.

**Inputs:** Front 1

**Expects:** any (data / value op)

**Variables:** `scale` (10.0)

## Notes

**Posterize / colour quantize** — `floor(c * scale) / scale` per channel snaps each channel to
`scale` discrete levels. (Despite the name, it's a 2D colour quantize, not a 3D voxel op.)

### Practical notes
- Lower `scale` = fewer, chunkier bands; higher = subtler. Turns smooth gradients into flats.
- Uses: cel / graphic-poster looks, banding tests, reducing an image to a few tones.
