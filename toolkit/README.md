# Research Writing Workbench Toolkit

This local release candidate contains nine focused Skills, deterministic governance CLIs, JSON Schemas, and reproducible archives. The integrated pack is a distribution container, not a Skill itself and not a public release.

## Choose a Skill

Start with `$research-writing-workbench` when a task spans stages. Use `$research-planning`, `$literature-discovery`, `$evidence-extract`, `$research-synthesis`, `$methodology-review`, `$research-writing`, `$research-export`, or `$research-risk-watch` when the input, output, and success condition are already clear.

## Build artifacts

- `agents-skills/<skill>/`: self-contained directory for repository or user Skill installation.
- `claude/<skill>-<version>.zip`: deterministic one-top-level-directory archive; compatibility depends on the target consumer.
- `pack-<version>.zip`: toolkit README, install guide, version, and every self-contained Skill.
- `checksums.sha256`: SHA-256 for every generated file except the manifest itself.

## Suggested research project directory

```text
research-project/
├─ source-catalog.json
├─ research-evidence.json
├─ corpus-snapshot.json
├─ findings.json
├─ checklist.json
├─ decision-log.json
├─ sources-private/       # never publish by default
├─ reports/
└─ exports/
```

## First small validation

From an installed Skill that includes the CLI and Schemas:

```powershell
python scripts/research_validate.py --project-dir <research-project>
python scripts/research_export.py --project-dir <research-project> --output <research-project>\exports\claims.md --dry-run
```

The repository development workflow uses `.venv`; packaged runtime scripts use only the Python standard library.

## Governance loop

1. Register sources with stable IDs, hashes, locators, access dates, verification, and license status.
2. Extract Evidence without mixing direct facts, derivations, inference, assumptions, or recommendations.
3. Write deterministic and AI-assisted analysis into Findings, never into core facts.
4. Synchronize review Findings into stable Checklist items.
5. Apply explicit human decisions with the resolution CLI and append-only Decision Log.
6. Export only active, reviewed or confirmed, source-grounded claims.

An unresolved high-priority Checklist item blocks normal export with exit code 8. `--force` can create a conspicuous warning artifact; it cannot close the item, approve evidence, or include otherwise ineligible claims.

## Exit codes

| Code | Meaning |
|---:|---|
| 0 | Success |
| 2 | CLI usage error |
| 3 | Input file error |
| 4 | Schema validation failure |
| 5 | Cross-file consistency failure |
| 6 | Transformation, build, or output failure |
| 8 | Unresolved mandatory human review |

## Limits

The toolkit does not perform ethics approval, peer review, legal clearance, final statistical review, or copyright clearance. It never makes local build success equivalent to public release or research effectiveness.
