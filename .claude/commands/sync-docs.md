---
description: Regenerate setups, validate, and sync CLAUDE.md + README + Live-Flame status
---

Sync this project's generated files and hand-maintained docs after a change to
`tools/generate_setups.py`. Follow these steps in order and report what changed at the end.

## Golden rule (never violate)
`tools/generate_setups.py` is the single source of truth. NEVER hand-edit a
`.pixel_expression_node` or a per-setup `.md` — change `tools/generate_setups.py` (the `SETUPS`,
`CATEGORY`, `DOCS`, `EXPECTS`, `NOTES` tables) and regenerate. The `.md` docs and node XML
are outputs.

## Steps

1. **Snapshot for drift detection.** Before regenerating, copy the current
   `setups/**/*.pixel_expression_node` files somewhere temporary (e.g. `/tmp/pe_snapshot/`,
   preserving relative paths) so you can diff after — a refactor that's meant to be
   byte-identical must stay byte-identical.

2. **Regenerate:** run `python3 tools/generate_setups.py`. It must finish with no
   `WARNING: missing DOCS/EXPECTS entries` lines — if any appear, add the missing
   `DOCS`/`EXPECTS` (and `CATEGORY`) entries for those setups and re-run.

3. **Validate:** run `python3 tools/validate_setups.py`. It MUST report **0 errors**. Resolve
   every error before continuing (warnings: judge case-by-case — unused vars / undefined
   identifiers are usually real bugs). Remember the validator now flags any variable/formula
   that shadows a built-in (`uv x y width height centre E PI`) or input (`r1`…); that class
   is a silent no-load in Flame, so treat it as a hard error.

4. **Drift check.** Diff the regenerated `.pixel_expression_node` files against the snapshot.
   Report any files that changed. If a change was meant to be a pure refactor (identical
   output), investigate any diff before proceeding.

5. **Reconcile the setup count.** Count generated setups (the validator prints
   "N setups checked"). Make that number match everywhere it appears in **CLAUDE.md**
   (the "All N …" line and the "## Folders (N setups)" heading) and **README.md**
   (the "N ready-to-load …" intro and the "current status: N setups …" line). Search for
   the old number to catch stragglers.

6. **Update the per-folder tables in `README.md`.** For any setup added, renamed, or
   whose variables changed, update its row (File / Use / Inputs / Variables-with-defaults) in
   the matching folder table. Variable names and defaults must match the generator.

7. **Update the Live-Flame status** in BOTH `CLAUDE.md` (the "## Live-Flame status" section)
   and the "Live-Flame status" note in `README.md`. Reflect what the user has
   confirmed this session: move confirmed-loading setups into "Verified loading"; record any
   load/compile failure and its fix under "Fixed, awaiting re-confirm"; keep the
   "Not yet compile-checked" list accurate. Don't claim a setup is verified unless the user
   actually confirmed it loads.

8. **Verify table completeness for new setups.** Every setup in `SETUPS` should have matching
   `CATEGORY`, `DOCS`, and `EXPECTS` entries (the generator warns on missing DOCS/EXPECTS).
   `NOTES` is optional — add one only when a setup's value isn't obvious from its one-line use
   case, and keep trivial ops (e.g. `matte_combine` booleans) brief.

9. **Report.** Summarise: validator result (errors/warnings), setup count, which docs you
   edited, any node-file drift, and any setups still needing a live compile-check.

If `$ARGUMENTS` is given, treat it as extra focus for this run (e.g. a folder name to pay
special attention to, or "verified: <setup>" to mark a setup confirmed-loading).
