# Phase: champi-ai-cli Foundation

## Goal
A new `champi-ai-cli` package exists with a working CLI, orchestrator, and Claude adapter that can wire champi-imgui + champi-stt + champi-tts into a single coordinated session.

## Deliverables

### Backend
- [ ] New repo: `champi-ai/champi-ai-cli` with `src/champi_ai_cli/` package layout
- [ ] `cli.py`: Click-based CLI with subcommands: `start`, `status`, `discover`, `canvas`
- [ ] `orchestrator.py`: `ChampiOrchestrator` that subscribes to ImgUIEventTypes, STT, and TTS event lanes via champi-signals; dispatches to registered handlers; maintains session state (open canvases, active streams)
- [ ] `adapters/base.py`: `ModelAdapter` ABC with methods `on_tool_call_start`, `on_canvas_update`, `on_speech`, `respond`
- [ ] `adapters/claude.py`: `ClaudeAdapter` implementation using Anthropic SDK
- [ ] `adapters/openai.py`: `OpenAIAdapter` stub (interface only, raises NotImplementedError)
- [ ] `examples/jarvis_demo.py`: wires champi-imgui canvas (chat UI) + champi-stt (WhisperLive) + champi-tts (Kokoro) via ChampiOrchestrator + ClaudeAdapter; wake word "hey champi"

### Infrastructure
- [ ] `pyproject.toml` with dependencies: `click`, `champi-signals`, `champi-ipc`, `champi-imgui`, `anthropic`
- [ ] Dev dependencies: `pytest`, `ruff`, `mypy`
- [ ] CI workflow (GitHub Actions): lint + type check + test
- [ ] `champi-cli` entry point in pyproject.toml

### Validation
- [ ] Unit tests for ChampiOrchestrator event dispatch (mocked signal lanes)
- [ ] Unit tests for ClaudeAdapter (mocked Anthropic SDK)
- [ ] CLI smoke test: `champi-cli --help` returns 0
- [ ] Integration test: orchestrator discovers a running champi-imgui canvas via RENDER_FRAME lane

## Done Definition
- `pip install champi-ai-cli` installs the package and `champi-cli` is on PATH
- `champi-cli start` launches champi-imgui with signals wired
- `champi-cli status` queries running actors via health lanes and prints results
- `champi-cli discover` prints active lane registrations
- `ChampiOrchestrator.on_event(event_type, handler)` correctly dispatches events to registered handlers
- `ClaudeAdapter` sends prompts to Anthropic API and routes responses to TTS + canvas
- `jarvis_demo.py` runs end-to-end with all three champi packages installed

## Parallel work
- BE: `ModelAdapter` ABC + `ClaudeAdapter` can be written in parallel with `ChampiOrchestrator`
- BE: CLI subcommands can be stubbed immediately while orchestrator internals are built
- INFRA: pyproject.toml + CI can be set up day 1 while all BE work proceeds

## Phase dependencies
- Requires: Phase: MCP Render Fix (RENDER_FRAME heartbeat for health monitoring)
- Requires: Phase: MCP System State Reporter (ImgUISignalManager, QUERY_STATE/STATE_RESPONSE for status/discover commands)
- Requires: champi-signals and champi-ipc to be published/installable

## Complexity
- Backend: L
- Frontend: N/A
- Infra: M

## Risks
- champi-stt and champi-tts signal integration may not be stable yet; Jarvis demo may need to stub those initially
- Anthropic SDK async patterns may conflict with champi-signals' synchronous event dispatch; may need an async bridge
- New repo bootstrap means no existing CI, tests, or linting — higher initial overhead
- The orchestrator's "discover" feature depends on champi-ipc lane registry, which may not expose a discovery API yet
