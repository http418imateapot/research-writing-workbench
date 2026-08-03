# Data Contracts

All governed JSON uses JSON Schema draft 2020-12. The canonical schemas live in `shared/schemas/`; build-time whitelists copy only the schemas each Skill needs into `assets/schemas/`.

## Responsibility layers

| File | Responsibility | Must not do |
|---|---|---|
| `source-catalog.json` | Stable source IDs, bibliographic facts, hashes, locators, bounded excerpts, access and status metadata. | Store unlicensed full text or treat unverified metadata as confirmed. |
| `research-evidence.json` | Source-linked Evidence and bounded Claims. | Create a formal Claim without reviewed, source-grounded Evidence. |
| `corpus-snapshot.json` | Date-bounded search and inclusion state. | Rewrite Source Catalog facts. |
| `findings.json` | Deterministic or AI-assisted analysis with method ID, version, inputs, output, severity, and limitations. | Modify the core research model. |
| `checklist.json` | Stable, idempotent human-review workflow. | Auto-close an item or erase history. |
| `decision-log.json` | Append-only reviewer decisions and waivers. | Accept anonymous or incomplete waivers. |

## Source and Evidence rules

- Use a stable `source_id`, SHA-256, locator, bounded excerpt, excerpt hash, access date, verification status, and license status.
- Keep `explicit`, `derived`, `inference`, `assumption`, and `recommendation` separate.
- A reviewed or confirmed active Claim needs at least one reviewed Evidence record, and every linked Evidence needs a valid source reference.
- A formal Claim that uses `derived` Evidence additionally requires a recorded reproducible derivation.
- Preserve conflicting versions or sources with their IDs; do not silently overwrite them.

## CTCC compatibility

The Markdown engineering artifacts retain the established contracts:

- maturity: `planned`, `captured`, `reproduced`, `reviewed`, `invalidated`;
- claim type: `implementation`, `behavior`, `comparison`, `mechanism`, `transfer`;
- researcher decision: `keep`, `narrow`, `rework`, `withdraw`;
- unresolved marker: `[未取得產物]`, `[尚未重現]`, `[執行衝突]`, `[待研究者裁定]`.

The JSON governance layer does not reinterpret or automatically promote those states.

## Finding, Checklist, and decision rules

Checklist fingerprints depend on the stable Finding identity, method version, and affected IDs, not source content hashes. When a source hash changes, synchronization reopens a closed item while preserving history. Only `research_resolve.py` can apply explicit item decisions; all decisions require reviewer, date, and reason, while waivers also require approver and approval date.

## Formal export gate

Normal export includes only active, reviewed or confirmed, source-grounded claims. Any unresolved high-priority Checklist item returns exit code 8. `--force` produces a warning artifact but does not change state or include ineligible claims. The sidecar lists input hashes, included and excluded IDs, warnings, limitations, and output SHA-256.
