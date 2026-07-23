# ao_multiply

**What it does:** Multiplies beauty by an AO pass; `amount` blends it in, `aoGamma` shapes it.

**Use case:** Apply ambient occlusion in comp with control.

**Inputs:** Front 1 = beauty, Matte 1 = AO

**Expects:** scene-linear (AO on Matte 1 is data)

**Variables:** `amount` (1.0), `aoGamma` (1.0)

## Node dependencies
**Pipeline:** beauty (Front 1) + AO (Matte 1) → **this node**

Consumes specific **render AOVs/passes** delivered by your renderer or extracted from EXR layers upstream (a Read/MUX/Channel node). The passes are data/light — keep them in the right space (linear for light math) and wire each to the input named below. The **AO pass goes on Matte 1** (it's data, not a matte to key).

See `documentation/node_dependencies.md` for the full wiring guide.

## Notes

Multiplies the beauty by an **ambient-occlusion** pass, with controls to dial it in:
`amount` blends from off (1.0) to full AO, `aoGamma` shapes the contact-shadow falloff.

### Practical notes
- **Front 1 = beauty, Matte 1 = AO.** (AO rides on Matte 1, like depth.)
- `amount` 0..1 is the "how dirty" knob — 0 disables it, 1 is full multiply.
- `aoGamma` < 1 **deepens** the contact shadows, > 1 **lightens** them.
- Multiply belongs in **scene-linear**; the AO pass itself is data (0..1 occlusion).
