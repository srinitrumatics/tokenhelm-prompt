# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

<!-- SPECKIT START -->
Active feature: **Prompt Intelligence** (`001-prompt-intelligence`).
For technologies, project structure, and design decisions, read the current plan:
`specs/001-prompt-intelligence/plan.md` (with `research.md`, `data-model.md`,
`contracts/`, and `quickstart.md` alongside it).
<!-- SPECKIT END -->

## What this repository is

A **GitHub Spec Kit** project configured for Spec-Driven Development (SDD). At
present it contains **only the SDD tooling** — there is no application source
code, build system, or test suite yet. Those get created later, once a feature
spec is turned into a plan and implemented. Do not invent build/lint/test
commands; until real code exists, the only commands are the `/speckit-*`
workflow steps below.

Script type for this project is **PowerShell (`ps`)** and the coding-agent
integration is **claude** (see `.specify/integration.json`).

## The Spec-Driven Development workflow

Work flows through a fixed sequence of user-invocable skills (slash commands).
Each consumes the artifact the previous one produced. Run them in order:

1. `/speckit-constitution` — fill in `.specify/memory/constitution.md` with the
   project's governing principles. Currently an unfilled template; do this first.
2. `/speckit-specify` — turn a natural-language feature description into a spec.
   Creates `specs/NNN-<short-name>/spec.md` and records the active feature in
   `.specify/feature.json`. Specs describe **WHAT/WHY**, never HOW (no tech
   stack, no implementation detail).
3. `/speckit-plan` — produce the implementation plan for the active feature
   (the HOW: tech stack, structure, decisions).
4. `/speckit-tasks` — break the plan into actionable, ordered tasks.
5. `/speckit-implement` — execute the tasks and write the actual code.

Optional quality gates: `/speckit-clarify` (de-risk an ambiguous spec, run
before `/speckit-plan`), `/speckit-checklist` (validate requirements, after
plan), `/speckit-analyze` (cross-artifact consistency, after tasks). There is
also `/speckit-taskstoissues` to push tasks to GitHub issues.

The full chain is registered as the `speckit` workflow
(`.specify/workflows/workflow-registry.json`).

## How the pieces fit together

- **`.claude/skills/speckit-*/SKILL.md`** — the actual instructions executed for
  each slash command. These are the source of truth for what each step does; read
  the relevant `SKILL.md` before running or modifying a step.
- **`.specify/templates/`** — the templates each step copies and fills in
  (`spec-template.md`, `plan-template.md`, `tasks-template.md`,
  `checklist-template.md`, `constitution-template.md`).
- **`.specify/memory/constitution.md`** — project principles. Loaded by
  `/speckit-specify` and `/speckit-plan` as governing constraints, so keep it
  current.
- **`.specify/feature.json`** — written by `/speckit-specify`; tells downstream
  steps which feature directory is active. Feature directories are independent of
  git branch names.
- **`specs/NNN-<short-name>/`** — one directory per feature (sequential numbering
  per `.specify/init-options.json`), holding that feature's `spec.md`, `plan.md`,
  `tasks.md`, and `checklists/`.

### Extension hooks

`.specify/extensions.yml` defines hooks the skills fire automatically. The
`agent-context` extension runs `after_specify` and `after_plan` to refresh agent
context (`auto_execute_hooks: true`). When editing a `SKILL.md`, preserve its
Pre-/Post-Execution hook handling — those blocks dispatch these hooks.

## Conventions

- When modifying a workflow step, edit its `.claude/skills/speckit-*/SKILL.md`,
  not a copy. The templates and skills are bundled assets kept in sync with the
  installed CLI version.
- The `<!-- SPECKIT START -->` / `<!-- SPECKIT END -->` block above is managed by
  Spec Kit's agent-context extension — leave its markers intact.
