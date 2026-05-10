# Documentation Index

Complete documentation for Champi-Gen-UI MCP Server.

---

## 📖 Getting Started

1. **[README.md](../README.md)** - Project overview and quick start guide
2. **[PLAN_SUMMARY.md](../PLAN_SUMMARY.md)** - Executive summary of the complete plan
3. **[IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md)** - Detailed implementation roadmap

---

## 🏗️ Architecture & Design

4. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete system architecture
   - Component architecture
   - Data flow diagrams
   - State management
   - Threading model
   - Extension system
   - Serialization format

---

## 📋 API References

5. **[MCP_TOOLS_API.md](MCP_TOOLS_API.md)** - All 200+ MCP tools documented
   - Canvas management tools
   - Widget tools (all categories)
   - Animation tools
   - Extension tools
   - Input/output tools
   - Complete parameter schemas

6. **[IMGUI_CORE_REFERENCE.md](IMGUI_CORE_REFERENCE.md)** - ImGui API reference
   - All ImGui core functions
   - Widget APIs
   - Drawing APIs
   - Input handling
   - Style & theming APIs
   - 200+ function signatures

---

## 🎨 Widget & Extension Guides

7. **[WIDGET_CATALOG.md](WIDGET_CATALOG.md)** - Complete widget listing
   - 150+ widgets categorized
   - Basic widgets (buttons, text, inputs)
   - Data widgets (tables, trees, lists)
   - Visualization widgets (plots, charts)
   - Custom widgets (knobs, toggles, spinners)
   - Container widgets (windows, panels)

8. **[EXTENSIONS_GUIDE.md](EXTENSIONS_GUIDE.md)** - Third-party extension integration
   - imgui_club (memory editor, multi-context)
   - HImGuiAnimation (keyframe animations)
   - File dialogs (ImGuiFD, imfile)
   - Notifications (imgui-notify)
   - Node editors
   - Text/code editors
   - Plotting library (ImPlot)
   - Custom widgets collection

---

## 🔧 Workflow Guides

9. **[TEMPLATE_WORKFLOW.md](TEMPLATE_WORKFLOW.md)** - Template management workflow
   - When to save templates (only when UI is complete)
   - Template creation best practices
   - Loading and reusing templates
   - Template organization strategies
   - Error handling and troubleshooting

---

## 📊 Quick Reference

### By Topic

#### Canvas & Rendering
- Canvas modes → [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md#21-canvas-system-mode-based)
- Canvas tools → [MCP_TOOLS_API.md](MCP_TOOLS_API.md#1-canvas-management-7-tools)
- Rendering architecture → [ARCHITECTURE.md](ARCHITECTURE.md#6-canvas-system-architecture)

#### Widgets
- Widget catalog → [WIDGET_CATALOG.md](WIDGET_CATALOG.md)
- Widget architecture → [ARCHITECTURE.md](ARCHITECTURE.md#5-widget-system-architecture)
- Widget tools → [MCP_TOOLS_API.md](MCP_TOOLS_API.md#2-basic-widgets-25-tools)

#### Extensions
- Extension guide → [EXTENSIONS_GUIDE.md](EXTENSIONS_GUIDE.md)
- Extension architecture → [ARCHITECTURE.md](ARCHITECTURE.md#7-extension-integration)
- Extension tools → [MCP_TOOLS_API.md](MCP_TOOLS_API.md) (various sections)

#### Animation
- Animation system → [EXTENSIONS_GUIDE.md](EXTENSIONS_GUIDE.md#2-animation-system-himguianimation)
- Animation tools → [MCP_TOOLS_API.md](MCP_TOOLS_API.md#6-animation-tools-10-tools)
- Animation architecture → [ARCHITECTURE.md](ARCHITECTURE.md#8-animation-system)

#### Data & State
- State management → [ARCHITECTURE.md](ARCHITECTURE.md#3-state-management)
- Data binding → [ARCHITECTURE.md](ARCHITECTURE.md#9-data-binding-system)
- Serialization → [ARCHITECTURE.md](ARCHITECTURE.md#10-serialization-format)

---

## 🎯 By Use Case

### I want to...

#### Create UI
1. Read [README.md](../README.md#-usage-examples) for examples
2. Check [MCP_TOOLS_API.md](MCP_TOOLS_API.md) for available tools
3. Browse [WIDGET_CATALOG.md](WIDGET_CATALOG.md) for widgets

#### Add Animations
1. Read [EXTENSIONS_GUIDE.md](EXTENSIONS_GUIDE.md#2-animation-system-himguianimation)
2. Check [MCP_TOOLS_API.md](MCP_TOOLS_API.md#6-animation-tools-10-tools)

#### Plot Data
1. Read [EXTENSIONS_GUIDE.md](EXTENSIONS_GUIDE.md#63-plotting-extensions)
2. Check [MCP_TOOLS_API.md](MCP_TOOLS_API.md#10-plotting-tools-15-tools)
3. Browse [WIDGET_CATALOG.md](WIDGET_CATALOG.md#plotting-widgets-implot)

#### Create Node Graphs
1. Read [EXTENSIONS_GUIDE.md](EXTENSIONS_GUIDE.md#61-node-editors)
2. Check [MCP_TOOLS_API.md](MCP_TOOLS_API.md#11-node-editor-tools-10-tools)

#### Style & Theme
1. Read [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md#34-styling--theming-tools)
2. Check [MCP_TOOLS_API.md](MCP_TOOLS_API.md#5-styling--theming-12-tools)
3. Review [IMGUI_CORE_REFERENCE.md](IMGUI_CORE_REFERENCE.md#18-style--colors)

#### Save/Load UI
1. Read [ARCHITECTURE.md](ARCHITECTURE.md#10-serialization-format)
2. Check [MCP_TOOLS_API.md](MCP_TOOLS_API.md#17-exportimport-tools-8-tools)
3. Follow [TEMPLATE_WORKFLOW.md](TEMPLATE_WORKFLOW.md) for template management

#### Extend System
1. Read [ARCHITECTURE.md](ARCHITECTURE.md#7-extension-integration)
2. Review [EXTENSIONS_GUIDE.md](EXTENSIONS_GUIDE.md#8-integration-summary)

---

## 📚 Reference Tables

### Widget Count by Category
| Category | Count | Reference |
|----------|-------|-----------|
| Basic Widgets | 25+ | [WIDGET_CATALOG.md](WIDGET_CATALOG.md#basic-input-widgets) |
| Selection Widgets | 10+ | [WIDGET_CATALOG.md](WIDGET_CATALOG.md#selection-widgets) |
| Slider/Drag Widgets | 15+ | [WIDGET_CATALOG.md](WIDGET_CATALOG.md#slider--drag-widgets) |
| Color Widgets | 5+ | [WIDGET_CATALOG.md](WIDGET_CATALOG.md#color-widgets) |
| Container Widgets | 5+ | [WIDGET_CATALOG.md](WIDGET_CATALOG.md#container-widgets) |
| Table Widgets | 10+ | [WIDGET_CATALOG.md](WIDGET_CATALOG.md#table-widgets) |
| Plotting Widgets | 15+ | [WIDGET_CATALOG.md](WIDGET_CATALOG.md#plotting-widgets-implot) |
| Node Editor | 10+ | [WIDGET_CATALOG.md](WIDGET_CATALOG.md#node-editor-widgets) |
| Custom Widgets | 10+ | [WIDGET_CATALOG.md](WIDGET_CATALOG.md#custom-extended-widgets) |
| **Total** | **150+** | [WIDGET_CATALOG.md](WIDGET_CATALOG.md) |

### MCP Tool Count by Category
| Category | Count | Reference |
|----------|-------|-----------|
| Canvas Management | 7 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#1-canvas-management-7-tools) |
| Basic Widgets | 25 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#2-basic-widgets-25-tools) |
| Container Widgets | 5 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#3-container-widgets-5-tools) |
| Layout Tools | 10 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#4-layout-tools-10-tools) |
| Styling & Theming | 12 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#5-styling--theming-12-tools) |
| Animation Tools | 10 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#6-animation-tools-10-tools) |
| File Dialogs | 5 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#7-file-dialog-tools-5-tools) |
| Notifications | 7 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#8-notification-tools-7-tools) |
| Tables | 10 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#9-table-tools-10-tools) |
| Plotting | 15 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#10-plotting-tools-15-tools) |
| Node Editor | 10 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#11-node-editor-tools-10-tools) |
| Text Editor | 8 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#12-text-editor-tools-8-tools) |
| Memory Editor | 5 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#13-memory-editor-tools-5-tools) |
| Input Handling | 10 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#14-input-handling-tools-10-tools) |
| Drawing Tools | 15 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#15-drawing-tools-15-tools) |
| Data Binding | 8 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#16-data-binding-tools-8-tools) |
| Export/Import | 8 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#17-exportimport-tools-8-tools) |
| Custom Widgets | 10 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#18-custom-widgets-10-tools) |
| Advanced Features | 8 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#19-advanced-features-8-tools) |
| Utility Tools | 7 | [MCP_TOOLS_API.md](MCP_TOOLS_API.md#20-utility-tools-7-tools) |
| **Total** | **200+** | [MCP_TOOLS_API.md](MCP_TOOLS_API.md) |

### Extension Library Count
| Extension | Type | Reference |
|-----------|------|-----------|
| imgui_club | Multi-tools | [EXTENSIONS_GUIDE.md](EXTENSIONS_GUIDE.md#1-imgui-club-extensions) |
| HImGuiAnimation | Animation | [EXTENSIONS_GUIDE.md](EXTENSIONS_GUIDE.md#2-animation-system-himguianimation) |
| ImGuiFD | File Dialog | [EXTENSIONS_GUIDE.md](EXTENSIONS_GUIDE.md#31-imgui fd) |
| imfile | File Browser | [EXTENSIONS_GUIDE.md](EXTENSIONS_GUIDE.md#32-imfile-rust-based-alternative) |
| imgui-notify | Notifications | [EXTENSIONS_GUIDE.md](EXTENSIONS_GUIDE.md#4-notifications-imgui-notify) |
| Useful Widgets | Custom Widgets | [EXTENSIONS_GUIDE.md](EXTENSIONS_GUIDE.md#5-useful-widgets-collection) |
| ImNodes | Node Editor | [EXTENSIONS_GUIDE.md](EXTENSIONS_GUIDE.md#61-node-editors) |
| ImGuiColorTextEdit | Text Editor | [EXTENSIONS_GUIDE.md](EXTENSIONS_GUIDE.md#62-text-editors) |
| ImPlot | Plotting | [EXTENSIONS_GUIDE.md](EXTENSIONS_GUIDE.md#63-plotting-extensions) |
| Custom Collection | Knobs/Toggles/etc | [EXTENSIONS_GUIDE.md](EXTENSIONS_GUIDE.md#7-custom-widget-extensions) |
| **Total** | **10+** | [EXTENSIONS_GUIDE.md](EXTENSIONS_GUIDE.md) |

---

## 🔍 Search Tips

### Finding Specific Information

**Looking for a widget?**
→ [WIDGET_CATALOG.md](WIDGET_CATALOG.md) (Ctrl+F widget name)

**Looking for an MCP tool?**
→ [MCP_TOOLS_API.md](MCP_TOOLS_API.md) (Ctrl+F tool name)

**Looking for ImGui function?**
→ [IMGUI_CORE_REFERENCE.md](IMGUI_CORE_REFERENCE.md) (Ctrl+F function name)

**Looking for an extension?**
→ [EXTENSIONS_GUIDE.md](EXTENSIONS_GUIDE.md) (Ctrl+F extension name)

**Looking for architecture details?**
→ [ARCHITECTURE.md](ARCHITECTURE.md) (Ctrl+F component name)

**Looking for implementation details?**
→ [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) (Ctrl+F feature name)

---

## 📝 Documentation Conventions

### File Naming
- **UPPERCASE.md** - Top-level project docs (root directory)
- **Title_Case.md** - Reference documentation (docs directory)
- All docs use `.md` (Markdown) format

### Content Structure
- **H1 (#)** - Document title
- **H2 (##)** - Major sections
- **H3 (###)** - Subsections
- **H4 (####)** - Details

### Code Examples
- Python code blocks use \`\`\`python
- JSON examples use \`\`\`json
- Inline code uses \`backticks\`

### Links
- Internal links use relative paths
- External links use full URLs
- Anchors use lowercase with hyphens

---

## 🗂️ File Tree

```
champi-gen-ui/
├── README.md                      # Project overview
├── IMPLEMENTATION_PLAN.md         # Implementation roadmap
├── PLAN_SUMMARY.md                # Executive summary
├── RENDERING_INFRASTRUCTURE.md    # Rendering system docs
├── docs/
│   ├── INDEX.md                   # This file
│   ├── ARCHITECTURE.md            # System architecture
│   ├── MCP_TOOLS_API.md           # MCP tools reference
│   ├── WIDGET_CATALOG.md          # Widget listing
│   ├── EXTENSIONS_GUIDE.md        # Extensions guide
│   ├── TEMPLATE_WORKFLOW.md       # Template workflow guide
│   └── IMGUI_CORE_REFERENCE.md    # ImGui API reference
├── fast-mcp-docs/
│   ├── full-documentation.txt     # FastMCP docs
│   └── sitemap.txt                # FastMCP sitemap
└── imgui-docs/
    ├── flgt.pdf                   # FLGT manual
    ├── hello_imgui_manual.pdf     # Hello ImGui manual
    └── imgui_bundle_manual.pdf    # ImGui Bundle manual
```

---

## 📈 Documentation Stats

- **Total Documents**: 9 markdown files
- **Total Pages**: ~110+ pages
- **Total Words**: ~55,000+ words
- **Widgets Documented**: 150+
- **MCP Tools Documented**: 200+
- **ImGui Functions**: 200+
- **Extensions Covered**: 10+

---

## 🔄 Documentation Updates

This documentation is comprehensive but may be updated as the project evolves. Check the git history for changes:

```bash
git log -- docs/
```

---

## 📧 Feedback

Found an error or have a suggestion? Please open an issue or submit a pull request!

---

**Last Updated**: 2025-10-03
**Version**: 1.0 (Planning Phase)
