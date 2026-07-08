<!-- Thanks for contributing to AI-Ultimate-Shadowrocket -->

## What & why

<!-- Describe the change and the motivation. Link related issues. -->

## Type

- [ ] feat  - [ ] fix  - [ ] docs  - [ ] refactor  - [ ] test  - [ ] chore

## Checklist

- [ ] I edited `config/AI-Ultimate.template.conf` and/or `rules/*.list` — **not** the
      generated `config/AI-Ultimate.conf` directly.
- [ ] `python3 scripts/build.py` regenerated the config and I committed the result.
- [ ] `python3 scripts/validate.py` passes.
- [ ] `python3 -m unittest discover -s tests` passes.
- [ ] If I changed rule order, group strategy, or a routing decision, I updated
      `docs/` (and added/updated an ADR) and `CHANGELOG.md`.
- [ ] AI groups remain **Select-only** (no url-test / fallback / load-balance).
- [ ] Total strategy groups still ≤ 10.
