# Canetinhas — Project Brief

> Loaded automatically every session. This is a **documentation-only** project (research/reference Markdown + generated Office docs), not application code.

## What this is

A documentation set about **weight-loss injectable medications** — the "canetas emagrecedoras"
(GLP-1 / incretin-class drugs and related peptides). Plain-language research dossiers grounded in
official and peer-reviewed sources, so the reader arrives well-informed to a medical consultation.
The user is Portuguese-speaking (Brazil) and overweight, weighing options — the tone is informative,
**not** medical advice, and always points to professional follow-up.

## Repo layout

- `Pesquisas/` — research dossiers per drug/topic (e.g. `Retatrutida.md`)
- `md2docx.py` — repo-root tooling: stdlib-only Markdown → `.docx` generator (see below)

## Working conventions (follow without being re-asked)

1. **Preserve old versions.** Never overwrite a published doc — create a new variant with a `_v2` / `_v3` suffix.
2. **Bilingual.** Provide both **English** and **Canadian French** (`_FR` source files). Keep product names untranslated.
3. **Formats.** Deliver Word (`.docx`) and, where tabular, Excel (`.xlsx`) alongside the Markdown source.
4. **Naming.** Use exact official product/vendor naming conventions and current terminology. Keep config keys, CLI commands, and install paths as-is.
5. **Verify against docs.** Ground technical claims in current official documentation. The user actively fact-checks and supplies authoritative URLs — follow them.

## Environment gotchas

- **No pandoc, no `pip install`, no `sudo`.** Office files are generated with stdlib-only Python: `md2docx.py` (Markdown → `.docx`). If an xlsx generator or bulk find/replace helper is needed, recreate it stdlib-only (don't reach for python-docx/openpyxl/pandoc).
- **`/mnt/c` WSL mount throws flaky `statx` errors** on post-write checks. `/home/carlos/git/Canetinhas` points to the **same repo** and is more reliable — edit via that path, or apply bulk edits with a Python script that asserts edit counts.

## Persistent memory

Longer-form context lives in the memory folder indexed by
`/home/carlos/.claude/projects/-mnt-c-git-Canetinhas/memory/MEMORY.md`.
