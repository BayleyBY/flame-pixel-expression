# radar_sweep

**What it does:** Rotating radar/oscilloscope sweep around Centre with an exponential afterglow trailing behind the line, plus faint range rings; animate `sweep` 0→2π.

**Use case:** Radar/sonar HUDs, sci-fi scanner overlays, oscilloscope looks.

**Inputs:** none (uses Centre)

**Expects:** any — generates data/values

**Variables:** `sweep` (animated), `decay` (3.0), `ringFreq` (0.02), `glowR` (0.1), `glowG` (1.0), `glowB` (0.3)

## Notes

A **radar / oscilloscope sweep**: a bright line rotates around the **Centre**, trailing a
phosphor afterglow that fades the further behind the line you are, over faint range rings.

### How it works
- `gap = mod(sweep − pixelAngle, 2π)` is the **angular distance behind** the sweep line (0 at the
  line, growing all the way round). `exp(−gap·decay)` is the afterglow — bright at the line,
  decaying smoothly behind it.
- `rings` adds faint concentric range rings from radius (`length` to Centre) at `ringFreq`.
- The trail and rings are tinted by `glowR/glowG/glowB` (default phosphor green); OutMatte is the
  combined brightness.

### Practical notes
- **`sweep` is the keyframed clock** (0 → 2π over frames 1–100 = one full revolution) — scrub to
  spin it. Reverse the keys to sweep the other way; extend past 2π for multiple turns.
- `decay` sets afterglow length (higher = shorter, tighter trail); `ringFreq` sets range-ring
  spacing. Recolour via `glowR/glowG/glowB`.
- Generated look (tag Raw/Data). Screen it over a HUD/background; OutMatte drives glow or comps
  the sweep on its own.
