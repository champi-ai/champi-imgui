"""Widget implementations for champi-imgui.

This package contains all widget implementations organized by category:
- basic: Basic I/O widgets (buttons, text, checkboxes, etc.)
- input: Advanced input widgets (combos, lists, etc.)
- color: Color picker and editor widgets
- progress: Progress bars and loading indicators
- display: Display and visualization widgets (plot lines, colored text, etc.)
- container: Layout containers (windows, groups, tabs, etc.)
- slider: Numeric slider and drag controls
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
    "DragFloatWidget",
    "DragIntWidget",
    "DummyWidget",
    "GroupWidget",
    "HelpMarkerWidget",
    "InputDoubleWidget",
    "InputFloatWidget",
    "InputIntWidget",
    "InputScalarWidget",
    "InputTextWidget",
    "InvisibleButtonWidget",
    "LabelTextWidget",
    "ListBoxWidget",
    "LoadingIndicatorWidget",
    "PlotLinesWidget",
    "ProgressBarWidget",
    "RadioButtonWidget",
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
    "WindowWidget",
]
