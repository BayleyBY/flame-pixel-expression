# matte_xor

**What it does:** Exclusive-or of two mattes.

**Use case:** Keep only the non-overlapping parts.

**Inputs:** Matte 1 + Matte 2

**Expects:** any (data / value op)

_No variables._

## Notes

Exclusive-or of two mattes — white only where **exactly one** is white (the overlap cancels).
Inputs on Matte 1 and Matte 2.

### Quick test
Two overlapping shapes on **Matte 1 + Matte 2** → both shapes white with the **overlap
punched out black**. Only Matte 1 wired = pass-through (`m2` = 0).
