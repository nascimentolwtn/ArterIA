# Changelog

All notable changes to ArterIA are documented in this file, in plain language for anyone following the project (not just contributors). Versioning follows [Semantic Versioning](https://semver.org/) once the project has a first runnable release; before that, versions mark planning milestones.

## [0.1] - 2026-10-24

### Added

- Initial project documentation: `README.md` describing the project's purpose, workflow, and pilot city (São José dos Campos, SP, Brazil).
- Research brief (`docs/research-brief-sjc.md`) covering local context, academic foundations, and a recommended method for the first pilot.
- Architecture Decision Record process (`docs/adr/`), with ADR 0001 recording the choice of SUMO as the project's traffic simulator.
- Project guidance file (`CLAUDE.md`) for AI-assisted development sessions.
- Working notes convention (`.claude/napkin.md`) for tracking open items during development.
- Phased roadmap (`docs/roadmap.md`): "remote" work is now a list of tasks the owner can hand to Claude from the phone app (drafting, coding against small test fixtures, reviews, docs), while simulation runs, GUI tools and private data stay on the desktop. The earlier plan built around GitHub Actions runners was dropped.
