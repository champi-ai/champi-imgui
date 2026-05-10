"""Widget implementations for champi-imgui.

This package contains all widget implementations organized by category:
- basic: Basic I/O widgets (buttons, text, checkboxes, etc.)
- input: Advanced input widgets (combos, lists, etc.)
- color: Color picker and editor widgets
- progress: Progress bars and loading indicators
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

__all__ = [
    # Basic widgets
    "ArrowButtonWidget",
    "BulletTextWidget",
    "BulletWidget",
    "ButtonWidget",
    # Input widgets
    "CheckboxFlagsWidget",
    "CheckboxWidget",
    # Color widgets
    "ColorButtonWidget",
    "ColorEdit3Widget",
    "ColorEdit4Widget",
    "ColorPicker3Widget",
    "ColorPickerWidget",
    "ComboWidget",
    "InputDoubleWidget",
    "InputFloatWidget",
    "InputIntWidget",
    "InputScalarWidget",
    "InputTextWidget",
    "InvisibleButtonWidget",
    "LabelTextWidget",
    "ListBoxWidget",
    # Progress widgets
    "LoadingIndicatorWidget",
    "ProgressBarWidget",
    "RadioButtonWidget",
    "SelectableWidget",
    "SmallButtonWidget",
    "StatusBarWidget",
    "TextColoredWidget",
    "TextDisabledWidget",
    "TextWidget",
    "TextWrappedWidget",
]
