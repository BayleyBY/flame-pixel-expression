# lift_gamma_gain

**What it does:** Master tonal grade: `gain` (mult), `lift` (offset), then `gamma`.

**Use case:** Primary grade of shadows/mids/highlights.

**Inputs:** Front 1

**Expects:** scene-linear, or your grading space

**Variables:** `lift` (0.0), `gamma` (1.0), `gain` (1.0)

## Notes

The **primary tonal grade**: one control each for highlights, shadows, and midtones. The
order baked in is `pow(value * gain + lift, 1/gamma)`.

### What each knob does
- **`gain`** — a multiply; its effect grows with brightness, so it pivots on black and
  mostly moves the **highlights** (white point).
- **`lift`** — an add; a constant push that's most visible in the **shadows** (black point),
  fading out toward the highlights.
- **`gamma`** — a power curve that bends the **midtones** while leaving 0 and 1 roughly
  anchored — brightening or darkening the mids without crushing or clipping the ends.

### Practical notes
- **Workflow:** set `gain` for the highlights, `lift` for the shadows, then `gamma` to taste
  on the mids — that's the order the math applies and the order that converges fastest.
- This is a luma-style master grade on all three channels equally; for a colour cast use
  `white_balance`, for a single-hue fix use `hsl_targeted`.
- Defaults (`lift` 0, `gamma` 1, `gain` 1) are a no-op, so it's safe to drop in and dial.

### Quick test
Loads neutral (0 / 1 / 1) — no change on load is correct. `gamma` 1.5 → mids brighten,
black/white points hold; `lift` 0.1 → blacks go grey; `gain` 0.5 → whites halve.
