# Frontend Specification: N/A

This project is a Python library (champi-imgui) with a CLI entry point. There is no web frontend.
The "frontend" from the LLM perspective is the MCP tool API and the ImGui canvas windows.

## MCP Tool API (Section 7 — API Contract)

All existing MCP tools are documented in `docs/MCP_TOOLS_API.md`.

New tools added by the completion phases are specified in `docs/specs/backend.md` Section 7.

## ImGui Canvas (visual output)

ImGui canvas windows are created and managed by the champi-imgui MCP server. The visual output is
the canvas window rendered by hello_imgui on the user's display. No web frontend is involved.

## champi-ai-cli UX

The `champi-cli` command-line interface is the human-facing entry point for the ecosystem.
It is a Click CLI — no web UI. The Jarvis demo (`examples/jarvis_demo.py`) uses:
- champi-imgui canvas as the visual UI
- champi-stt for voice input
- champi-tts for voice output
- ChampiOrchestrator as the coordination layer
