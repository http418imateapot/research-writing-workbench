# Migration to 1.0

Version 1.0.0 preserves the `research-writing-workbench` name, CTCC states, claim types, researcher decisions, unresolved markers, Markdown templates, and legacy CLI flags. The major version reflects the canonical source-path migration and the new governed toolkit architecture.

| Previous file or function | New canonical location or behavior | Package | Compatibility risk |
|---|---|---|---|
| `.agents/skills/research-writing-workbench/` | `skills/research-writing-workbench/` | Built into `dist/agents-skills/research-writing-workbench/` | Source path changed; install the generated directory for repository discovery. |
| One repository Skill | Nine focused Skills with the original name as router | Each Skill has an independent package | Trigger selection expands; the original trigger remains. |
| Skill-only deterministic ZIP | `build.py`, per-Skill ZIPs, integrated pack, and manifest | `dist/` | Old `package_skill.py --output-dir` remains available. |
| Markdown-only evidence records | Optional governed JSON Source, Evidence, Snapshot, Finding, Checklist, and Decision Log | Whitelisted schemas per Skill | Existing Markdown inputs remain valid; JSON is additive. |
| `python scripts/check_all.py` | Same command through `.venv`; now also runs compile, pytest, and build check | Repository only | System Python execution is no longer the documented workflow. |
| `README.en.md` English primary | `README.md` English primary and `README.zh-TW.md` Traditional Chinese | Integrated pack uses toolkit README | `README.en.md` remains a compatibility link. |

The build excludes `.git`, `.venv`, tests, CI, fixtures, examples, `.work`, prompts history, private sources, reports, exports, and other non-whitelisted material from individual Skill packages.
