# Maintenance

Read the root [AGENTS.md](../AGENTS.md). Edit Skill instructions only in `skills/`, shared Schemas and rules only in `shared/`, and deterministic logic only in `scripts/` or `build.py`. Do not edit `dist/`.

Run the full `.venv` command set in AGENTS.md for every user-visible change. Validate every Skill with the available official Skill validator, run the built-in repository validator, perform the privacy scan, build twice, and compare all ZIP SHA-256 values.

When adding a Skill or dependency, update the explicit build maps, agents metadata, prompt-template, docs, tests, CHANGELOG, and package self-containment checks. New allowlist entries require a documented public and safe reason; never use an allowlist to hide a real secret or private identifier.
