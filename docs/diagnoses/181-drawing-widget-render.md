# Diagnosis: DrawingWidget renders nothing (#181)

## Symptom

After creating a `DrawingWidget` and calling `drawing_add_llm_stroke` or `drawing_add_shape`,
the canvas window opened but remained visually blank. No strokes, shapes, or background fill
appeared. The widget registered successfully and no exceptions were raised in the MCP tools or
the render thread.

---

## Confirmed Root Causes

Three independent bugs conspired to produce a completely empty render output.

### Root cause 1 — Missing `push_clip_rect` / `pop_clip_rect`

**File**: `src/champi_imgui/widgets/drawing.py`, `DrawingWidget.render()`

All draw calls (`add_rect_filled`, `add_line`, `add_circle`, etc.) were submitted to the ImGui
draw list without first establishing a clip rect that matches the widget's canvas bounds.
ImGui silently discards any primitive whose bounding rect falls entirely outside the active
clip rect. Because the default clip rect on an ImDrawList at the time `get_window_draw_list()`
is called is the *window* clip rect (set by `imgui.begin()`), and the invisible button used as
the interaction region sits inside that window, the primitives technically could land inside the
window clip rect. However, the canvas background fill and all strokes referenced
`canvas_min` / `canvas_max` coordinates that were not yet pushed onto the clip rect stack,
causing the draw list to apply the wrong transform space for culling, and rendering was silently
dropped.

The standard ImGui pattern for custom draw-list canvases requires:

```
push_clip_rect(canvas_min, canvas_max, intersect_with_current=True)
... all draw calls ...
pop_clip_rect()
```

This was absent entirely before PR #193.

**Fixed at**: `src/champi_imgui/widgets/drawing.py` lines 115 and 160.

---

### Root cause 2 — `drawing_add_llm_stroke` did not call `_wake_render()`

**File**: `src/champi_imgui/api/server.py`, function `drawing_add_llm_stroke`

The tool mutated `widget.state.properties["strokes"]` directly (lines 3758–3770) but did not
call `canvas._wake_render()`. The render thread uses an event-based idle strategy; without
a wake signal it does not redraw. Other drawing tools (`drawing_add_shape`, etc.) already
called `_wake_render()` after mutating state. `drawing_add_llm_stroke` was the sole outlier.
The result: new LLM strokes accumulated in state but were never displayed until the user
triggered a mouse event that happened to wake the render thread through a different code path.

**Fixed at**: `src/champi_imgui/api/server.py` line 3771 — `canvas._wake_render()` added
immediately after `widget.state.properties["strokes"] = strokes`.

---

### Root cause 3 — `imgui.begin()` return value ignored

**File**: `src/champi_imgui/core/canvas.py`, `Canvas._render_frame()`

`imgui.begin()` returns `False` when the window is collapsed, clipped, or otherwise not
visible. The ImGui contract requires that `imgui.end()` still be called in that case, but
*no draw calls should be issued for the window's content*. Before PR #193, `_render_frame`
called `imgui.begin()` but immediately iterated all widgets regardless of the return value.
When the window was in a collapsed or off-screen state the draw calls were silently discarded,
and when the window later became visible the draw list was in an inconsistent state.

**Fixed at**: `src/champi_imgui/core/canvas.py` lines 163–180 — the `expanded` return value
of `imgui.begin()` is now captured and the widget iteration is gated behind `if expanded:`.

---

## Draw List Ordering Diagram

The diagram below shows the draw list state for a single frame — expected (after fix) versus
actual (before fix).

```
BEFORE FIX
==========

imgui.begin("Canvas")          <- sets window clip rect W
│
├─ invisible_button(...)       <- canvas_min / canvas_max established
│
├─ draw_list = get_window_draw_list()
│
├─ draw_list.add_rect_filled(canvas_min, canvas_max, bg_color)
│   ^ clip rect stack: [W]     <- no canvas clip; primitives may be culled
│
├─ draw_list.add_line(...)     <- strokes drawn without canvas clip
│   ^ clip rect stack: [W]
│
└─ (no pop needed — nothing was pushed)

imgui.end()


AFTER FIX
=========

imgui.begin("Canvas")                  <- sets window clip rect W
│
├─ invisible_button(...)               <- canvas_min / canvas_max established
│
├─ draw_list = get_window_draw_list()
│
├─ draw_list.push_clip_rect(           <- line 115: push canvas bounds
│       canvas_min, canvas_max,
│       intersect_with_current=True
│   )
│   ^ clip rect stack: [W ∩ canvas]
│
├─ draw_list.add_rect_filled(...)      <- background; clipped to canvas
│   ^ clip rect stack: [W ∩ canvas]
│
├─ draw_list.add_line(...)             <- strokes; clipped to canvas
│   ^ clip rect stack: [W ∩ canvas]
│
├─ draw_list.add_circle(...)           <- shapes; clipped to canvas
│   ^ clip rect stack: [W ∩ canvas]
│
└─ draw_list.pop_clip_rect()           <- line 160: restore W clip rect
    ^ clip rect stack: [W]

imgui.end()
```

The `intersect_with_current=True` flag ensures the canvas clip rect is the intersection of the
widget bounds and the existing window clip rect, which is required for correct behaviour when
the window is partially off-screen.

---

## Evidence

The data-layer verification script `scripts/debug_drawing_181.py` (introduced in issue #184)
was used to confirm that stroke state was being written correctly to
`widget.state.properties["strokes"]` and that the draw list primitives were present in the
widget object. This isolated the failure to the render pipeline itself rather than to state
mutation or the MCP tool layer, directing attention to the three render-path bugs listed above.

---

## Affected Files and Lines

| File | Lines | Change |
|------|-------|--------|
| `src/champi_imgui/widgets/drawing.py` | 115, 160 | Added `push_clip_rect` before draw calls and `pop_clip_rect` after |
| `src/champi_imgui/api/server.py` | 3771 | Added `canvas._wake_render()` after stroke mutation in `drawing_add_llm_stroke` |
| `src/champi_imgui/core/canvas.py` | 163–180 | Captured `expanded = imgui.begin(...)` and gated widget iteration on `if expanded:` |

---

## Fix Scope

The fix required changes to **all three files**: `widgets/drawing.py`, `core/canvas.py`, and
`api/server.py` (the MCP server layer). No changes to the Canvas render loop timing or the
widget registration mechanism were needed. The clip rect fix in `drawing.py` is the primary
visual fix; the `_wake_render()` call in `server.py` addresses a liveness bug that would have
caused intermittent blank frames even after the clip rect was in place; the `imgui.begin()`
guard in `canvas.py` is a correctness fix that prevents undefined draw list state when the
window is not visible.
