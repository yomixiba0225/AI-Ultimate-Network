# IMPLEMENTATION_PLAN.md

**Phase:** 5 — Implementation Plan (milestones)
**Project:** AI-Ultimate-Network
**Status:** M1–M6 executed in the v0.1.0 build; M7 (push/release) pending user confirmation.

Each milestone lists **Deliverables · Dependencies · Acceptance Criteria · Rollback**.
Milestones map to the gap clusters in `GAP_ANALYSIS.md` §7 and the design in `DESIGN.md` §9.

---

## M1 — Repository Cleanup ✅

**Deliverables**
- Directory layout per ARCH §4: `config/ rules/ scripts/ tests/ docs/ docs/adr/ .github/ assets/`.
- Baseline moved to `config/lazy.conf` (kept as reference/rollback).
- `.gitignore` (ignores node/subscription secrets, `.DS_Store`, Python caches).
- `LICENSE` (MIT).

**Dependencies** — none (foundational).

**Acceptance** — tree matches ARCH §4; baseline preserved unmodified; no secrets tracked.

**Rollback** — directory ops are reversible; baseline file untouched in content.

---

## M2 — Rule Providers ✅

**Deliverables**
- `rules/anthropic.list`, `openai.list`, `github.list`, `google.list`, `apple.list`,
  `ai-extra.list`, `china.list`, `proxy.list` — per-vendor source of truth.
- Seeds derived from the audited `AI.txt` (46 rules) + the granular block that was commented
  out in the baseline.

**Dependencies** — M1.

**Acceptance** — every list parses (comments/blanks stripped); Claude and OpenAI live in
**separate** files; Apple Intelligence domains relocated out of the AI bundle.

**Rollback** — delete `rules/`; template `#!INCLUDE`s become the only affected lines.

---

## M3 — Strategy Groups ✅

**Deliverables**
- `config/AI-Ultimate.template.conf` `[Proxy Group]` with 8 groups.
- AI groups (`Claude/ChatGPT/GitHub/Google`) = `select`; `Auto` = `url-test` (non-AI only).
- `Apple = select, DIRECT, Proxy`; `Final = select, Proxy, DIRECT`.

**Dependencies** — M2 (groups referenced by rules).

**Acceptance** — ≤10 groups; AI groups Select-only; validator passes group checks; config
imports in Shadowrocket.

**Rollback** — revert the `[Proxy Group]` block; rules still parse (they'd reference missing
groups → caught by validator, so revert template as a unit).

---

## M4 — Regex ✅

**Deliverables**
- `policy-regex-filter` per group with `\bXX\b` region matching (TW/US/SG/JP + zh variants).
- Documented optional `policy-select-name=` preferred-node pin (no hardcoding).

**Dependencies** — M3.

**Acceptance** — each AI group regex compiles (validator); adding a fake `台湾107`-style node
name auto-matches Claude in principle (regex verified); US does not match AUS.

**Rollback** — replace regex filters with manual node references; revert template.

---

## M5 — Validation ✅

**Deliverables**
- `scripts/build.py` (+ `--check` freshness mode).
- `scripts/validate.py` (9 checks incl. FINAL-last, dangling refs, canonical order).
- `tests/test_config.py` (13 stdlib unittest cases).
- `.github/workflows/validate.yml` (build → freshness → validate → tests).
- Optional DNS-over-proxy + `ipv6` notes, plus a Clash Global Script IPv6 consistency guard.

**Dependencies** — M3, M4.

**Acceptance** — `build.py` regenerates deterministically; `validate.py` exits 0; all tests
pass; CI green.

**Rollback** — tooling is additive; removing it does not affect the config.

---

## M6 — Documentation ✅

**Deliverables**
- `README.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, this plan.
- ADR-0001…0006 (Claude-TW, ChatGPT-US, Apple-DIRECT, AI-Select-only, regex-nodes, fork-vs-subscription).
- Issue/PR templates.

**Dependencies** — M1–M5 (docs describe them).

**Acceptance** — a newcomer can understand architecture, strategy, build, validation, and
release from the repo alone (Master §Final Objective).

**Rollback** — docs are additive.

---

## M7 — Release ⏳ (requires user confirmation)

**Deliverables**
- `git init` + conventional-commit history.
- Tag `v0.1.0` + GitHub release notes (from CHANGELOG).
- Push to `github.com/yomixiba0225/AI-Ultimate-Network`.

**Dependencies** — M1–M6; **quality gates green**.

**Acceptance** — repo pushes; CI passes on GitHub; config URL importable in Shadowrocket.

**Rollback** — pre-push: local only, fully revertible. Post-push: `git revert` + re-tag; the
config URL can be repointed or the release deleted.

> ⚠️ Per Master Task and engineering guidelines, **push and release are NOT performed
> automatically**. They wait for explicit user confirmation ("Ready to push?").

---

## Execution order & gating

```
M1 ─▶ M2 ─▶ M3 ─▶ M4 ─▶ M5 ─▶ M6 ─▶ M7(confirm)
                         │
                  quality gate: build --check && validate && tests
                  any red  ─▶  stop, fix, do not proceed
```

Small, readable, conventional commits; document every change; never a large rewrite; prefer
extension over replacement.
