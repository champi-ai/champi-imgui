# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v1.1.0 (2026-05-10)

### Feat

- **server**: add MCP tools for all widget types
- **server**: add MCP tools for all widget types (#33)
- add coverage reporting, badge generation, and 55% threshold (#34)
- **widgets**: implement plotting widgets module via ImPlot (#32)
- **widgets**: implement display widgets module
- **widgets**: add container widgets module
- **widgets**: add slider widgets module (SliderFloat, SliderInt, DragFloat, DragInt)
- add core widget system with basic, color, input, progress widgets

### Fix

- use renewed RELEASE_TOKEN for push and release creation (#43)
- consolidate --no-raise codes on cz global args to fix exit code 18 (#42)
- handle tag already exists on release retry (#41)
- open PR for bump commit instead of pushing directly to protected main (#40)
- use GITHUB_TOKEN for release workflow push (#39)
- prevent CI re-trigger loop from badge commit using job condition and concurrency (#38)
- use credential store so cz bump push authenticates on self-hosted runner (#37)
- use contextlib.suppress in test teardown to satisfy SIM105
- clean .venv on each run and use uv for security job

## v1.0.1 (2025-10-30)

### Fix

- make version test dynamic to prevent failures on releases (#5)

## v1.0.0 (2025-10-30)

### BREAKING CHANGE

- First feature commit, bumps version v0.0.3 → v0.1.0

### Feat

- implement core canvas system with shared memory IPC (#4)

## v0.0.3 (2025-10-30)

### Fix

- use correct tag format with v prefix in GitHub release (#2)

## v0.0.2 (2025-10-30)

### Fix

- remove changelog_start_rev to fix first release
- handle first release without previous tags in release workflow

## v0.0.0 (2025-10-26)

### Feat

- Initial commit with repository structure
