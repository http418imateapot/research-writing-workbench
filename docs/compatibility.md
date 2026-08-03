# Compatibility

Version 1.0.0 preserves the public `research-writing-workbench` Skill name, CTCC states, claim types, researcher decisions, unresolved markers, Markdown templates, `package_skill.py --output-dir`, and existing CLI failure behavior. It adds eight focused Skills and governed JSON contracts.

Canonical authoring moved from `.agents/skills/` to `skills/`. Build output under `dist/agents-skills/` is the self-contained installation source for repository or user Skill locations. See [migration](MIGRATION-1.0.md).

Runtime CLI code uses the Python standard library. Repository development and CI use Python 3.12 and 3.13 through `.venv`; other versions or platforms are not claimed until actually tested. Deterministic ZIP structure is product-neutral, but platform import behavior must be verified against the target host.
