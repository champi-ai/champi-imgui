# Champi-Gen-UI Architecture

## System Overview

Champi-Gen-UI is an MCP (Model Context Protocol) server that bridges LLMs with ImGui for generative UI creation. It provides 200+ tools for creating, manipulating, and rendering UI elements through natural language.

---

## Core Components

### 1. MCP Server Layer
```
┌─────────────────────────────────────────┐
│         FastMCP Server                   │
│  ┌─────────────────────────────────┐   │
│  │   Tool Registry (200+ tools)    │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │   Request Handler               │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │   Response Serializer           │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│      Canvas Manager                      │
│  ┌─────────────────────────────────┐   │
│  │   Canvas Registry               │   │
│  │   Canvas State Store            │   │
│  │   Rendering Pipeline            │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│      Widget System                       │
│  ┌─────────────────────────────────┐   │
│  │   Widget Registry               │   │
│  │   Widget Factory                │   │
│  │   Widget State Manager          │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│      ImGui Bundle                        │
│  ┌─────────────────────────────────┐   │
│  │   imgui (core)                  │   │
│  │   immapp (application)          │   │
│  │   ImPlot (plotting)             │   │
│  │   Extensions                    │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## 2. Data Flow

### Request Flow
```
LLM → MCP Client → FastMCP Server → Tool Handler → Canvas Manager → Widget System → ImGui
```

### Response Flow
```
ImGui → Widget State → Canvas State → Serializer → FastMCP Server → MCP Client → LLM
```

### Render Loop
```
Main Thread:
  ├─ Process MCP Commands (from queue)
  ├─ Update Widget States
  ├─ Run ImGui Frame
  │   ├─ Begin Frame
  │   ├─ Render Widgets
  │   ├─ Handle Input
  │   └─ End Frame
  └─ Swap Buffers

Worker Threads:
  ├─ MCP Request Handler
  ├─ Command Queue Writer
  └─ State Synchronizer
```

---

## 3. State Management

### Canvas State
```python
@dataclass
class CanvasState:
    canvas_id: str
    mode: CanvasMode  # standard, docking, multi_viewport, fullscreen, overlay
    size: tuple[int, int]
    position: tuple[int, int]
    theme: str
    widgets: dict[str, WidgetState]
    layout: LayoutState
    style: StyleState
    active: bool
```

### Widget State
```python
@dataclass
class WidgetState:
    widget_id: str
    widget_type: str
    properties: dict[str, Any]
    position: tuple[float, float]
    size: tuple[float, float]
    visible: bool
    enabled: bool
    parent: Optional[str]
    children: list[str]
    callbacks: dict[str, str]
    data_bindings: dict[str, DataBinding]
```

### Signal-Based Updates
Uses `blinker` for event-driven state propagation:

```python
# Signals
widget_created = blinker.signal('widget-created')
widget_updated = blinker.signal('widget-updated')
widget_deleted = blinker.signal('widget-deleted')
canvas_updated = blinker.signal('canvas-updated')
state_changed = blinker.signal('state-changed')
```

---

## 4. Threading Model

### Thread Architecture
```
┌─────────────────────────────────────────┐
│           Main Thread                    │
│  - ImGui Rendering                       │
│  - Input Handling                        │
│  - Command Processing                    │
│  - State Updates                         │
└─────────────────────────────────────────┘
           ▲         │
     Commands    State Updates
           │         ▼
┌─────────────────────────────────────────┐
│         Worker Thread Pool               │
│  - MCP Request Handling                  │
│  - Tool Execution                        │
│  - Data Processing                       │
│  - Background Tasks                      │
└─────────────────────────────────────────┘
```

### Thread-Safe Communication
```python
# Command queue (worker → main)
command_queue = Queue()

# State queue (main → worker)
state_queue = Queue()

# Thread-safe state access
state_lock = threading.RLock()
```

---

## 5. Widget System Architecture

### Widget Factory Pattern
```python
class WidgetFactory:
    def __init__(self):
        self._creators: dict[str, Callable] = {}

    def register(self, widget_type: str, creator: Callable):
        self._creators[widget_type] = creator

    def create(self, widget_type: str, **props) -> Widget:
        creator = self._creators.get(widget_type)
        if not creator:
            raise ValueError(f"Unknown widget type: {widget_type}")
        return creator(**props)

# Registration
factory = WidgetFactory()
factory.register("button", ButtonWidget)
factory.register("text", TextWidget)
factory.register("slider", SliderWidget)
```

### Widget Base Class
```python
class Widget(ABC):
    def __init__(self, widget_id: str, **props):
        self.widget_id = widget_id
        self.properties = props
        self.state = WidgetState(...)

    @abstractmethod
    def render(self):
        """Render the widget using ImGui calls"""
        pass

    @abstractmethod
    def update(self, **props):
        """Update widget properties"""
        pass

    def serialize(self) -> dict:
        """Serialize widget state to JSON"""
        return self.state.__dict__
```

---

## 6. Canvas System Architecture

### Canvas Manager
```python
class CanvasManager:
    def __init__(self):
        self.canvases: dict[str, Canvas] = {}
        self.active_canvas: Optional[str] = None

    def create_canvas(self, canvas_id: str, **props) -> Canvas:
        canvas = Canvas(canvas_id, **props)
        self.canvases[canvas_id] = canvas
        return canvas

    def get_canvas(self, canvas_id: str) -> Canvas:
        return self.canvases.get(canvas_id)

    def render_all(self):
        for canvas in self.canvases.values():
            if canvas.active:
                canvas.render()
```

### Canvas Class
```python
class Canvas:
    def __init__(self, canvas_id: str, **props):
        self.canvas_id = canvas_id
        self.widgets: dict[str, Widget] = {}
        self.layout_manager = LayoutManager()
        self.state = CanvasState(...)

    def add_widget(self, widget: Widget):
        self.widgets[widget.widget_id] = widget
        widget_created.send(self, widget=widget)

    def render(self):
        """Render all widgets on this canvas"""
        imgui.begin(self.state.title)
        for widget in self.widgets.values():
            if widget.state.visible:
                widget.render()
        imgui.end()
```

---

## 7. Extension Integration

### Extension Registry
```python
class ExtensionRegistry:
    def __init__(self):
        self.extensions: dict[str, Extension] = {}

    def register(self, name: str, extension: Extension):
        self.extensions[name] = extension
        extension.initialize()

    def get(self, name: str) -> Extension:
        return self.extensions.get(name)

# Extensions
registry = ExtensionRegistry()
registry.register("implot", ImPlotExtension())
registry.register("node_editor", NodeEditorExtension())
registry.register("text_editor", TextEditorExtension())
registry.register("file_dialog", FileDialogExtension())
registry.register("notifications", NotificationExtension())
```

### Extension Base Class
```python
class Extension(ABC):
    @abstractmethod
    def initialize(self):
        """Initialize extension"""
        pass

    @abstractmethod
    def register_tools(self, server: FastMCP):
        """Register MCP tools"""
        pass

    @abstractmethod
    def render(self):
        """Render extension UI"""
        pass
```

---

## 8. Animation System

### Animation Engine
```python
class AnimationEngine:
    def __init__(self):
        self.animations: dict[str, Animation] = {}
        self.current_frame = 0

    def create_animation(self, anim_id: str, keyframes: list, values: list, easing: str):
        animation = Animation(anim_id, keyframes, values, easing)
        self.animations[anim_id] = animation

    def update(self, delta_time: float):
        self.current_frame += delta_time * 60  # Assume 60 FPS
        for animation in self.animations.values():
            if animation.playing:
                animation.update(self.current_frame)

    def get_value(self, anim_id: str) -> float:
        animation = self.animations.get(anim_id)
        return animation.get_interpolated_value() if animation else 0.0
```

### Animation Class
```python
class Animation:
    def __init__(self, anim_id: str, keyframes: list, values: list, easing: str):
        self.anim_id = anim_id
        self.keyframes = keyframes
        self.values = values
        self.easing = EasingFunction.get(easing)
        self.playing = False
        self.current_value = values[0]

    def get_interpolated_value(self) -> float:
        # Find surrounding keyframes
        # Apply easing function
        # Return interpolated value
        pass
```

---

## 9. Data Binding System

### Data Binding Architecture
```python
class DataBindingManager:
    def __init__(self):
        self.bindings: dict[str, DataBinding] = {}

    def bind(self, widget_id: str, property: str, data_source: DataSource):
        binding = DataBinding(widget_id, property, data_source)
        self.bindings[f"{widget_id}.{property}"] = binding
        data_source.on_change(lambda value: self.update_widget(widget_id, property, value))

    def update_widget(self, widget_id: str, property: str, value: Any):
        # Update widget with new value
        state_changed.send(self, widget_id=widget_id, property=property, value=value)
```

---

## 10. Serialization Format

### Canvas JSON Format
```json
{
  "version": "1.0",
  "canvas": {
    "canvas_id": "main_canvas",
    "mode": "standard",
    "size": [1280, 720],
    "position": [0, 0],
    "theme": "dark",
    "title": "My UI"
  },
  "widgets": [
    {
      "widget_id": "btn1",
      "type": "button",
      "properties": {
        "label": "Click Me",
        "position": [10, 10],
        "size": [100, 30]
      },
      "callbacks": {
        "on_click": "handle_click"
      }
    },
    {
      "widget_id": "slider1",
      "type": "slider_float",
      "properties": {
        "label": "Volume",
        "value": 0.5,
        "min": 0.0,
        "max": 1.0,
        "position": [10, 50]
      },
      "data_bindings": {
        "value": "audio.volume"
      }
    }
  ],
  "layout": {
    "type": "vertical",
    "spacing": 5,
    "padding": 10
  }
}
```

---

## 11. Error Handling

### Error Hierarchy
```python
class ChampiGenUIError(Exception):
    """Base exception"""
    pass

class CanvasError(ChampiGenUIError):
    """Canvas-related errors"""
    pass

class WidgetError(ChampiGenUIError):
    """Widget-related errors"""
    pass

class ToolError(ChampiGenUIError):
    """MCP tool execution errors"""
    pass
```

### Error Recovery
- Graceful degradation for missing widgets
- State rollback on failed operations
- Error reporting through MCP responses

---

## 12. Performance Considerations

### Optimization Strategies
1. **Widget Pooling**: Reuse widget objects
2. **Lazy Rendering**: Only render visible widgets
3. **State Diffing**: Only update changed properties
4. **Command Batching**: Batch multiple MCP commands
5. **Async Operations**: Non-blocking tool execution

### Memory Management
- Automatic cleanup of deleted widgets
- Canvas destruction clears all resources
- Texture caching for images

---

## 13. Testing Architecture

### Test Structure
```
tests/
├── unit/
│   ├── test_widgets.py
│   ├── test_canvas.py
│   ├── test_layout.py
│   └── test_animation.py
├── integration/
│   ├── test_mcp_tools.py
│   ├── test_extensions.py
│   └── test_serialization.py
└── visual/
    ├── test_rendering.py
    └── test_themes.py
```

---

## 14. Deployment Architecture

### MCP Server Configuration
```json
{
  "mcpServers": {
    "champi-gen-ui": {
      "command": "uv",
      "args": ["run", "champi-gen-ui", "serve"],
      "cwd": "/path/to/champi-gen-ui",
      "env": {
        "DISPLAY": ":0"
      }
    }
  }
}
```

### Server Entry Point
```python
# src/champi_gen_ui/server/main.py
from fastmcp import FastMCP

mcp = FastMCP("champi-gen-ui")

# Register all tools
register_canvas_tools(mcp)
register_widget_tools(mcp)
register_extension_tools(mcp)

if __name__ == "__main__":
    mcp.run()
```

---

This architecture provides a scalable, extensible foundation for generative UI creation through LLMs using ImGui and the MCP protocol.
