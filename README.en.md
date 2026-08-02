# Research Writing Workbench

[正體中文](README.md)

Research Writing Workbench is an open-source repository skill for software engineering, system integration, and event-driven systems research. It helps researchers turn code, tests, traces, logs, diffs, and execution records into reproducible, falsifiable, and bounded evidence.

**It is neither a general research methodology nor a paper generator.** Existing code does not prove correct behavior; a passing test does not prove general reliability; a diff does not prove causation; and buildability does not prove effectiveness. The researcher remains responsible for the question, validation contract, interpretation, and final claim.

## CTCC control loop

The project uses a Contract–Trace–Counterexample–Claim (CTCC) loop:

- **Contract:** define shared inputs, observable outputs, completion semantics, failures, timeouts, retries, ordering, concurrency, instrumentation, and fair comparison conditions.
- **Trace:** index versions, configuration, commands, exit codes, tests, events, traces, logs, and diffs required to reconstruct an execution.
- **Counterexample:** plan cases that can defeat the preferred explanation, including timeout, disconnection, duplication, reordering, concurrent overwrite, partial failure, and observability gaps.
- **Claim:** keep, narrow, rework, or withdraw a statement according to executed evidence and counterexamples.

See the [canonical Skill](.agents/skills/research-writing-workbench/SKILL.md), [architecture](docs/architecture.md), and [method origin and boundaries](docs/method-origin.md).

## Scope

The workbench targets software engineering and architecture, external API integration, event-driven and asynchronous systems, open-source tools, testing, failure reproduction, trace replay, AI-generated code auditing, and artifact-based design or case research.

## Quick start

```text
Use $research-writing-workbench to build a validation contract and counterexample matrix from the code, tests, and execution records I provide. Keep unexecuted work as planned and draft only claims supported by reproducible artifacts.
```

For environments without repository skills, use the [generic Traditional Chinese prompt](prompts/master-prompt.zh-TW.md). Run `python scripts/check_all.py` for repository checks. Passing checks do not establish research validity or general effectiveness.

Repository-authored content is licensed under [Apache-2.0](LICENSE). This license does not cover the referenced book, purchaser-only attachments, or other third-party material.
