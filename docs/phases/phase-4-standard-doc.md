# Phase 4: Org-Wide Standard Documentation

## Goal
Document the MCP server structural conventions adopted across champi-ai repositories so future projects follow the same patterns.

## Deliverables

### Backend
- [ ] N/A

### Frontend
- [ ] N/A

### Infrastructure
- [ ] Create `docs/MCP_SERVER_STRUCTURE.md` covering:
  - Directory layout convention (`api/server.py`, not `server/main.py`)
  - Factory pattern (`create_mcp_app(**overrides)`)
  - FastMCP lifespan for cleanup
  - CLI group structure (`serve`, `demo`, `validate`, `ipc cleanup`, `ipc status`)
  - Testing via factory injection (no monkeypatch globals)
  - Tool return shape (`{"success": bool, "data": dict, "error": str}`)
  - Logging to stderr convention
  - Entry point naming (`package.cli:cli`)

## Done Definition
- `docs/MCP_SERVER_STRUCTURE.md` exists and covers all 8 topics listed above
- Document references concrete champi-imgui examples for each pattern
- Document is valid Markdown (no broken links, proper headings)
- Document is under 300 lines (concise reference, not tutorial)

## Parallel work
- This phase can begin as soon as Phase 1 is merged (does not require Phase 2 or 3)

## Phase dependencies
- Requires: Phase 1 (factory pattern must be implemented to document it accurately)
- Soft dependency on Phase 2 (CLI section references click group)

## Complexity
- Backend: N/A
- Frontend: N/A
- Infra: S

## Risks
- Document may become outdated if patterns evolve before other repos adopt them
- Scope creep into tutorial territory (must stay as reference doc)
