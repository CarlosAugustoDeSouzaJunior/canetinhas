# Canetinhas — Project Brief

> Loaded automatically every session. This is a **documentation-only** project (research/reference Markdown + generated Office docs), not application code.

## What this is

<!-- TODO: fill in the project subject. This is a documentation set, same shape as the
     MSFabric project. Describe the domain, the audience, and what the docs cover. -->

_(Subject to be defined — replace this section with a short description of the domain,
the intended consumers, and the deliverables.)_

## Repo layout

- `md2docx.py` — repo-root tooling: stdlib-only Markdown → `.docx` generator (see below)
- _(Add directories as content is created, e.g. `Architecture/`, `Governance/`, `Archive/`.)_

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
