# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

ArterIA is an AI-assisted decision-support tool for street-network planning, built to be reusable across cities. It searches a constrained catalog of feasible interventions (one-way conversions, reversible lanes, bus lanes, lane reallocation, protected bike/pedestrian corridors, turn restrictions, a few new connectors) and evaluates each candidate package against a calibrated baseline traffic simulation, rather than letting an AI model freely invent street layouts. See `README.md` for the full pitch and workflow.

## Status

Early stage, pre-code. The repository currently holds planning and reference documentation only:

- `README.md` — project pitch, workflow, stack (pt-BR). `README-eng.md` is the English original; keep both in sync.
- `docs/research-brief-sjc.md` — research brief and methodology for the first pilot (São José dos Campos, SP, Brazil).
- `docs/adr/` — Architecture Decision Records for significant, hard-to-reverse decisions (see `docs/adr/README.md` for format and when to write one).
- `.claude/napkin.md` — running runbook of scratch notes, backlog, and open items only; completed items move to `CHANGELOG.md` and are removed from here.
- `CHANGELOG.md` — user-facing log of completed work, versioned starting at 0.1.

There are no build, lint, or test commands yet because there is no code yet.

## Architecture direction

Per the recommended method in `docs/research-brief-sjc.md` and `docs/adr/0001-traffic-simulator-choice.md`:

- **Stack:** SUMO (`netconvert`/`netedit` for OSM-based network builds, TraCI for runtime control) is the baseline traffic simulator and lower-level traffic-assignment engine. Python is the implementation language. See ADR 0001 for why SUMO was chosen over MATSim/AIMSUN/Vissim/TransModeler.
- **Per-city structure:** each city is meant to live under `cities/<city-name>/` with its own data, calibration, and scenarios, while optimizer and evaluation code stays shared across cities. This structure does not exist yet; follow it when adding the first pilot's code.
- **Two-level design:** an upper-level optimizer (genetic algorithm, Bayesian optimization, or RL) selects intervention packages; SUMO acts as the lower level, returning the traffic response (travel times, queues, transit performance, emissions/safety proxies) used to evaluate each package before/after.
- **Cities: Skylines** is a stakeholder-communication layer only, never the quantitative evidence base for a recommendation — see the "Important caution" and "Phase 6" sections of the research brief before using it.

## Working conventions

- Record any significant, hard-to-reverse decision (simulator/library choice, project structure, data schema) as a new ADR in `docs/adr/`, numbered sequentially.
- Keep `.claude/napkin.md` current: re-prioritize on read, cap at ~10 items per category, log only open/recurring/high-value notes (not completed work).
- **Language:** the user gives commands in English; code, commit messages, ADRs, and project docs stay in English (except `README.md`, which is pt-BR with `README-eng.md` as the English version). The thesis under `thesis/` is written in Brazilian Portuguese (pt-BR), per the `thesis-student` agent instructions.
- **Thesis documentation:** after every commit that changes code, docs, or ADRs, invoke the `thesis-student` agent (`.claude/agents/thesis-student.md`) to log progress in `thesis/progress-log.md` and update the outline/chapters under `thesis/`. The agent only writes inside `thesis/` and never commits; include its changes in the next commit or a follow-up `docs(thesis)` commit, following the commit-style rules in the global instructions. Skip for purely administrative commits.
- When work finishes, move it out of `.claude/napkin.md` and into `CHANGELOG.md` as a user-facing entry (plain language, under the current version), bumping the version if the change is release-worthy.
