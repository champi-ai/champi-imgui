"""Widget implementations for champi-imgui.

This package contains all widget implementations organized by category:
- basic: Basic I/O widgets (buttons, text, checkboxes, etc.)
- input: Advanced input widgets (combos, lists, etc.)
- color: Color picker and editor widgets
- progress: Progress bars and loading indicators
- display: Display and visualization widgets (plot lines, colored text, etc.)
- container: Layout containers (windows, groups, tabs, etc.)
- slider: Numeric slider and drag controls
- menu: Menu and navigation widgets (menu bar, menus, tree nodes, etc.)
- plotting: Advanced plotting widgets using ImPlot
"""

from champi_imgui.widgets.basic import (
    ArrowButtonWidget,
    BulletTextWidget,
    BulletWidget,
    ButtonWidget,
    CheckboxWidget,
    InputTextWidget,
    InvisibleButtonWidget,
    LabelTextWidget,
    SmallButtonWidget,
    TextColoredWidget,
    TextDisabledWidget,
    TextWidget,
    TextWrappedWidget,
)
from champi_imgui.widgets.color import (
    ColorButtonWidget,
    ColorEdit3Widget,
    ColorEdit4Widget,
    ColorPicker3Widget,
    ColorPickerWidget,
)
from champi_imgui.widgets.container import (
    ChildWindowWidget,
    CollapsingHeaderWidget,
    DummyWidget,
    GroupWidget,
    SeparatorWidget,
    SpacingWidget,
    TabBarWidget,
    TabItemWidget,
    WindowWidget,
)
from champi_imgui.widgets.display import (
    HelpMarkerWidget,
    ImageWidget,
    PlotLinesWidget,
)
from champi_imgui.widgets.input import (
    CheckboxFlagsWidget,
    ComboWidget,
    InputDoubleWidget,
    InputFloatWidget,
    InputIntWidget,
    InputScalarWidget,
    ListBoxWidget,
    RadioButtonWidget,
    SelectableWidget,
)
from champi_imgui.widgets.menu import (
    ContextMenuWidget,
    MenuBarWidget,
    MenuItemWidget,
    MenuWidget,
    PopupWidget,
    TooltipWidget,
    TreeNodeWidget,
)
from champi_imgui.widgets.plotting import (
    BarChartWidget,
    ErrorBarsWidget,
    HeatmapWidget,
    HistogramWidget,
    LineChartWidget,
    PieChartWidget,
    RealtimePlotWidget,
    ScatterPlotWidget,
)
from champi_imgui.widgets.progress import (
    LoadingIndicatorWidget,
    ProgressBarWidget,
    StatusBarWidget,
)
from champi_imgui.widgets.slider import (
    DragFloatWidget,
    DragIntWidget,
    SliderFloatWidget,
    SliderIntWidget,
)

__all__ = [
    "ArrowButtonWidget",
    "BarChartWidget",
    "BulletTextWidget",
    "BulletWidget",
    "ButtonWidget",
    "CheckboxFlagsWidget",
    "CheckboxWidget",
    "ChildWindowWidget",
    "CollapsingHeaderWidget",
    "ColorButtonWidget",
    "ColorEdit3Widget",
    "ColorEdit4Widget",
    "ColorPicker3Widget",
    "ColorPickerWidget",
    "ComboWidget",
    "ContextMenuWidget",
    "DragFloatWidget",
    "DragIntWidget",
    "DummyWidget",
    "ErrorBarsWidget",
    "GroupWidget",
    "HeatmapWidget",
    "HelpMarkerWidget",
    "HistogramWidget",
    "ImageWidget",
    "InputDoubleWidget",
    "InputFloatWidget",
    "InputIntWidget",
    "InputScalarWidget",
    "InputTextWidget",
    "InvisibleButtonWidget",
    "LabelTextWidget",
    "LineChartWidget",
    "ListBoxWidget",
    "LoadingIndicatorWidget",
    "MenuBarWidget",
    "MenuItemWidget",
    "MenuWidget",
    "PieChartWidget",
    "PlotLinesWidget",
    "PopupWidget",
    "ProgressBarWidget",
    "RadioButtonWidget",
    "RealtimePlotWidget",
    "ScatterPlotWidget",
    "SelectableWidget",
    "SeparatorWidget",
    "SliderFloatWidget",
    "SliderIntWidget",
    "SmallButtonWidget",
    "SpacingWidget",
    "StatusBarWidget",
    "TabBarWidget",
    "TabItemWidget",
    "TextColoredWidget",
    "TextDisabledWidget",
    "TextWidget",
    "TextWrappedWidget",
    "TooltipWidget",
    "TreeNodeWidget",
    "WindowWidget",
]
