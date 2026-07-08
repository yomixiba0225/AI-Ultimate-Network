# ADR-0005: Node selection by region regex, never hardcoded node names

- **Status:** Accepted
- **Date:** 2026-07-08

## Context
Charter Principle 5 / PRD §16 / ARCH §8: adding an airport node must require **zero** config
changes. Hardcoding node names ("台湾101, 台湾102, …") is explicitly forbidden and doesn't scale
across multiple airports. We also don't know the user's exact node names at design time — the
solution must be **node-name-agnostic** and work for anyone's airport.

## Decision
- Each group uses `policy-regex-filter` with a **bounded region regex**:
  - Taiwan `(?i)(\bTW\b|Taiwan|台湾|台灣)`
  - US `(?i)(\bUS\b|USA|美国|美國)` · SG `(?i)(\bSG\b|Singapore|新加坡|狮城)` · JP `(?i)(\bJP\b|Japan|日本)`
- **`\b` word boundaries** prevent cross-region bleed (e.g. `\bUS\b` does not match `AUS`).
- **Preferred node** is expressed with an optional `policy-select-name=<exact name>` — a single
  override point — instead of hardcoding names into rules.
- Regexes are validated to compile in `scripts/validate.py`.

## Consequences
- ✅ New nodes auto-join the correct group; removing nodes is safe.
- ✅ Works for any airport whose node names carry a region token.
- ⚠️ **Requires** node names to contain a region token; airports using opaque names need a
  per-airport alias (documented as a bounded workaround, not an architecture change).
- ⚠️ Regex correctness is empirical — the bug-report template asks for node naming to diagnose.
