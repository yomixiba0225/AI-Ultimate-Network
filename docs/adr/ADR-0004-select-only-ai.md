# ADR-0004: AI groups are Select-only (no url-test / fallback / load-balance)

- **Status:** Accepted
- **Date:** 2026-07-08

## Context
Charter Principle 1 (Stable IP First) and the Strategy Philosophy forbid automatic node
switching for AI services. Speed-testing and failover rotate IPs, which is exactly what breaks
Claude/ChatGPT sessions and reputation.

## Decision
- `Claude`, `ChatGPT`, `GitHub`, `Google` groups are **`select`** only.
- **Forbidden** for these groups: `url-test`, `fallback`, `load-balance`, `random`.
- The only auto-select group is `Auto` (`url-test`), used **exclusively** for non-AI generic
  traffic reachable via the `Proxy` group.
- This is **machine-enforced**: `scripts/validate.py` fails the build if any AI group uses a
  forbidden type; `tests/test_config.py` asserts it.

## Consequences
- ✅ AI IPs are stable by construction; the invariant can't silently regress.
- ✅ Users retain full manual control.
- ⚠️ Users must pick a node per AI group once (documented in README Quick Start).
