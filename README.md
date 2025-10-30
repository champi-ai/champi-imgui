# Champi-ImGui 🎨

> **Generative UI for LLMs through ImGui and Python**

An MCP (Model Context Protocol) server that enables Large Language Models to create sophisticated user interfaces using ImGui through natural language commands.

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0+-green.svg)](https://github.com/jlowin/fastmcp)
[![ImGui Bundle](https://img.shields.io/badge/ImGui-Bundle-red.svg)](https://github.com/pthom/imgui_bundle)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚧 Migration Status

**champi-imgui** is a clean migration from `champi-gen-ui` with the following improvements:
- ✅ Clean git history with meaningful commits
- ✅ Semantic versioning with conventional commits
- ✅ Automated CI/CD and release workflows
- ✅ Comprehensive pre-commit hooks and quality gates
- 🚧 **Currently at v0.0.3** - Infrastructure setup complete, feature migration in progress

See [MIGRATION_PLAN.md](MIGRATION_PLAN.md) for the detailed 8-stage migration roadmap.

---

## ✨ Planned Features

Once migration is complete, champi-imgui will provide:

- **200+ MCP Tools** for comprehensive UI creation
- **150+ Widget Types** from ImGui core and extensions
- **10+ Integrated Extensions** (plotting, node editing, file dialogs, etc.)
- **5 Canvas Modes** (standard, docking, multi-viewport, fullscreen, overlay)
- **Keyframe Animation System** with multiple easing functions
- **Data Binding** for reactive UI updates
- **JSON Serialization** for saving/loading UI definitions
- **Code Generation** to export standalone Python scripts
- **Template System** for reusable UI patterns

---

## 🚀 Quick Start

### Installation

```bash
uv pip install champi-imgui
```

Or with pip:
```bash
pip install champi-imgui
```

### Running the MCP Server

```bash
champi-imgui serve
```

### MCP Client Configuration

Add to your MCP client configuration (e.g., `.mcp.json`):

```json
{
  "mcpServers": {
    "champi-imgui": {
      "command": "uv",
      "args": ["run", "champi-imgui", "serve"],
      "cwd": "/path/to/champi-imgui"
    }
  }
}
```

---

## 💡 Usage Examples

### Example 1: Simple Button
```
LLM: "Create a button that says 'Click Me'"

MCP executes:
- create_canvas(canvas_id="main")
- add_button(canvas_id="main", widget_id="btn1", label="Click Me")
```

### Example 2: Data Dashboard
```
LLM: "Create a dashboard with a line chart showing sales data and a data table below"

MCP executes:
- create_canvas(canvas_id="dashboard", mode="docking")
- add_line_plot(canvas_id="dashboard", plot_id="sales_chart", ...)
- create_table(canvas_id="dashboard", table_id="sales_table", ...)
- set_layout_vertical(canvas_id="dashboard")
```

### Example 3: Node Editor
```
LLM: "Create a node graph editor for a processing pipeline"

MCP executes:
- create_canvas(canvas_id="pipeline")
- create_node_editor(canvas_id="pipeline", editor_id="graph")
- add_node(editor_id="graph", node_id="input", title="Input")
- add_node(editor_id="graph", node_id="process", title="Process")
- add_link(editor_id="graph", from_pin="input.out", to_pin="process.in")
```

---

## 📚 Documentation

Comprehensive documentation is available:

### Migration Documentation
- **[MIGRATION_PLAN.md](MIGRATION_PLAN.md)** - Complete 8-stage implementation roadmap
- **[MIGRATION_SYSTEM_PROMPT.md](MIGRATION_SYSTEM_PROMPT.md)** - Execution methodology for LLM assistants
- **[CLAUDE.md](CLAUDE.md)** - Development guide and project overview

### Reference Guides (Coming in future stages)
- **WIDGET_CATALOG.md** - All 150+ widgets documented
- **MCP_TOOLS_API.md** - Complete API for 200+ MCP tools
- **EXTENSIONS_GUIDE.md** - Third-party extension integration
- **ARCHITECTURE.md** - System architecture

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│             LLM                     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│        MCP Client                   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     FastMCP Server (200+ tools)     │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │   Canvas Manager    │
    └──────────┬──────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Widget System                  │
├─────────────────────────────────────┤
│    Widget Registry (150+)           │
│    Animation Engine                 │
│    Layout Manager                   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      ImGui Bundle                   │
│  - ImGui Core                       │
│  - ImPlot (plotting)                │
│  - Extensions (node editor, etc.)   │
└─────────────────────────────────────┘
```

---

## 🛠️ MCP Tool Categories

The server will provide 200+ tools organized into 20 categories:

1. **Canvas Management** (7 tools)
2. **Basic Widgets** (25 tools)
3. **Container Widgets** (5 tools)
4. **Layout Tools** (10 tools)
5. **Styling & Theming** (12 tools)
6. **Animation Tools** (10 tools)
7. **File Dialog Tools** (5 tools)
8. **Notification Tools** (7 tools)
9. **Table Tools** (10 tools)
10. **Plotting Tools** (15 tools)
11. **Node Editor Tools** (10 tools)
12. **Text Editor Tools** (8 tools)
13. **Memory Editor Tools** (5 tools)
14. **Input Handling Tools** (10 tools)
15. **Drawing Tools** (15 tools)
16. **Data Binding Tools** (8 tools)
17. **Export/Import Tools** (8 tools)
18. **Custom Widgets** (10 tools)
19. **Advanced Features** (8 tools)
20. **Utility Tools** (7 tools)

---

## 🧩 Widget Categories

### Basic Widgets (25+)
Buttons, text labels, input fields, checkboxes, radio buttons, sliders, drag controls, combo boxes, list boxes, color pickers, and more.

### Data Visualization (15+)
Line charts, scatter plots, bar charts, histograms, heatmaps, pie charts, candlestick charts, and more (via ImPlot).

### Advanced Widgets (30+)
Tables, tree views, node graphs, syntax-highlighted text editors, file dialogs, notifications, memory editors, and more.

### Custom Widgets (10+)
Knobs, toggles, spinners, date pickers, time pickers, gradient editors, and community-contributed widgets.

---

## 🔌 Extensions

Champi-ImGui integrates 10+ powerful extensions:

- **imgui_club** - Memory editor, multi-context compositor
- **HImGuiAnimation** - Keyframe animation system
- **ImGuiFD** - Lightweight file dialogs
- **imgui-notify** - Toast notification system
- **ImPlot** - Advanced plotting library
- **ImNodes** - Node graph editing
- **ImGuiColorTextEdit** - Syntax-highlighted editor
- **imgui-markdown** - Markdown rendering
- And more!

---

## 🖼️ Canvas Modes

1. **Standard** - Traditional window-based UI
2. **Docking** - Dockable window layout
3. **Multi-Viewport** - Multiple windows support
4. **Fullscreen** - Immersive full-screen mode
5. **Overlay** - Transparent overlay mode

---

## 💾 Data Persistence

### Export UI Definition
```python
export_ui_json(canvas_id="dashboard", file_path="dashboard.json")
```

### Import UI Definition
```python
import_ui_json(file_path="dashboard.json")
```

### Generate Python Code
```python
generate_code(canvas_id="dashboard", output_path="dashboard.py")
```

---

## ⚙️ Development

### Project Structure
```
champi-imgui/
├── src/champi_imgui/
│   ├── server/          # FastMCP server
│   ├── core/            # Core UI management
│   ├── widgets/         # Widget library
│   ├── extensions/      # Third-party integrations
│   ├── themes/          # Theming & styling
│   └── layout/          # Layout managers
├── docs/                # Documentation
├── tests/               # Test suite
├── .github/workflows/   # CI/CD pipelines
└── MIGRATION_PLAN.md    # Implementation roadmap
```

### Running Tests
```bash
# Install dev dependencies
uv sync --all-extras --dev

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=champi_imgui
```

### Code Quality
```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type checking
uv run mypy src

# Security scanning
uv run bandit -r src
```

---

## 🤝 Contributing

Contributions are welcome! The project uses:
- **Conventional Commits** for commit messages
- **Semantic Versioning** for releases
- **Pre-commit hooks** for code quality
- **GitHub Actions** for CI/CD

### Development Setup
```bash
# Clone repository
git clone https://github.com/champi-ai/champi-imgui.git
cd champi-imgui

# Install with UV
uv sync --all-extras --dev

# Install pre-commit hooks
pre-commit install
pre-commit install --hook-type commit-msg

# Run in development mode (when implemented)
uv run champi-imgui serve
```

---

## 📋 Requirements

- Python 3.12+ (also supports Python 3.13)
- imgui-bundle
- pyglm
- fastmcp
- blinker
- loguru

See [pyproject.toml](pyproject.toml) for complete dependencies.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Dear ImGui** - Amazing immediate mode GUI library
- **imgui-bundle** - Comprehensive Python bindings
- **FastMCP** - Excellent MCP server framework
- **ImPlot** - Powerful plotting library
- **champi-gen-ui** - Original implementation that inspired this clean migration

---

## 🔗 Related Projects

Part of the Champi project family:
- **champi-signals** - Signal management and event processing
- **champi-stt** - Multi-provider speech-to-text
- **champi-tts** - Multi-provider text-to-speech
- **champi-imgui** - Generative UI (this project)

---

## 💬 Support

- 📚 [Documentation](MIGRATION_PLAN.md)
- 🐛 [Issue Tracker](https://github.com/champi-ai/champi-imgui/issues)
- 💭 [Discussions](https://github.com/champi-ai/champi-imgui/discussions)

---

## 🗺️ Migration Roadmap

### Stage 1-3: Infrastructure ✅ (v0.0.3)
- Repository setup with clean git history
- Semantic versioning with commitizen
- CI/CD pipelines with GitHub Actions
- Pre-commit hooks for code quality

### Stage 4: Documentation 🚧 (stays v0.0.3)
- README.md and project documentation
- API reference structure

### Stage 5: Core System 📋 (v0.0.3 → v0.1.0)
- MCP server foundation
- Canvas system with IPC
- Basic widget infrastructure

### Stage 6: Widget Library 📋 (v0.1.0 → v0.2.0)
- Complete widget set (150+)
- Widget factory and registry
- MCP tool bindings

### Stage 7: Advanced Features 📋 (v0.2.0 → v0.3.0)
- Animation system
- Data binding
- Themes and layouts
- Template system

### Stage 8: Polish & Export 📋 (v0.3.0 → v0.4.0)
- JSON serialization
- Code generation
- Complete testing

See [MIGRATION_PLAN.md](MIGRATION_PLAN.md) for detailed implementation steps.

---

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

**Built with ❤️ using ImGui, Python, and FastMCP**
