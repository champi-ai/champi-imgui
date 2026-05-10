"""Tests for plotting widgets (ImPlot-based).

Tests cover all 8 plotting widgets:
- LineChartWidget
- BarChartWidget
- ScatterPlotWidget
- HistogramWidget
- HeatmapWidget
- PieChartWidget
- RealtimePlotWidget
- ErrorBarsWidget
"""

from champi_imgui.core.state import WidgetState
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

# ==============================================================================
# LineChartWidget Tests
# ==============================================================================


def test_line_chart_widget_creation_defaults():
    """Test LineChartWidget creation with default values."""
    widget = LineChartWidget("line-1")

    assert widget.widget_id == "line-1"
    assert isinstance(widget.state, WidgetState)
    assert widget.state.widget_type == "LineChartWidget"
    assert widget.state.properties["title"] == "Line Chart"
    assert widget.state.properties["x_data"] == []
    assert widget.state.properties["y_data"] == []
    assert widget.state.properties["line_label"] == "Line"


def test_line_chart_widget_creation_with_data():
    """Test LineChartWidget creation with data."""
    x_data = [0.0, 1.0, 2.0, 3.0]
    y_data = [0.0, 1.0, 0.5, 2.0]
    widget = LineChartWidget(
        "line-2",
        title="My Chart",
        x_data=x_data,
        y_data=y_data,
        line_label="Series A",
    )

    assert widget.state.properties["title"] == "My Chart"
    assert widget.state.properties["x_data"] == x_data
    assert widget.state.properties["y_data"] == y_data
    assert widget.state.properties["line_label"] == "Series A"


def test_line_chart_widget_visibility():
    """Test LineChartWidget visibility handling."""
    widget = LineChartWidget("line-3")

    assert widget.state.visible is True

    widget.set_visible(False)
    assert widget.state.visible is False


def test_line_chart_widget_serialization():
    """Test LineChartWidget serialization."""
    x_data = [1.0, 2.0]
    y_data = [3.0, 4.0]
    widget = LineChartWidget(
        "line-4", title="Serial Chart", x_data=x_data, y_data=y_data
    )

    data = widget.serialize()

    assert data["widget_id"] == "line-4"
    assert data["widget_type"] == "LineChartWidget"
    assert data["properties"]["title"] == "Serial Chart"
    assert data["properties"]["x_data"] == x_data
    assert data["properties"]["y_data"] == y_data


def test_line_chart_widget_update():
    """Test LineChartWidget property update."""
    widget = LineChartWidget("line-5")

    widget.update(x_data=[0.0, 1.0], y_data=[0.5, 1.5])

    assert widget.state.properties["x_data"] == [0.0, 1.0]
    assert widget.state.properties["y_data"] == [0.5, 1.5]


# ==============================================================================
# BarChartWidget Tests
# ==============================================================================


def test_bar_chart_widget_creation_defaults():
    """Test BarChartWidget creation with default values."""
    widget = BarChartWidget("bar-1")

    assert widget.widget_id == "bar-1"
    assert widget.state.widget_type == "BarChartWidget"
    assert widget.state.properties["title"] == "Bar Chart"
    assert widget.state.properties["values"] == []
    assert widget.state.properties["labels"] == []
    assert widget.state.properties["bar_label"] == "Bars"
    assert widget.state.properties["bar_width"] == 0.67


def test_bar_chart_widget_creation_with_data():
    """Test BarChartWidget creation with data."""
    values = [10.0, 20.0, 15.0]
    labels = ["A", "B", "C"]
    widget = BarChartWidget(
        "bar-2",
        title="Sales",
        values=values,
        labels=labels,
        bar_label="Revenue",
        bar_width=0.5,
    )

    assert widget.state.properties["values"] == values
    assert widget.state.properties["labels"] == labels
    assert widget.state.properties["bar_label"] == "Revenue"
    assert widget.state.properties["bar_width"] == 0.5


def test_bar_chart_widget_serialization():
    """Test BarChartWidget serialization."""
    widget = BarChartWidget("bar-3", values=[1.0, 2.0], labels=["X", "Y"])

    data = widget.serialize()

    assert data["widget_id"] == "bar-3"
    assert data["widget_type"] == "BarChartWidget"
    assert data["properties"]["values"] == [1.0, 2.0]


# ==============================================================================
# ScatterPlotWidget Tests
# ==============================================================================


def test_scatter_plot_widget_creation_defaults():
    """Test ScatterPlotWidget creation with default values."""
    widget = ScatterPlotWidget("scatter-1")

    assert widget.widget_id == "scatter-1"
    assert widget.state.widget_type == "ScatterPlotWidget"
    assert widget.state.properties["title"] == "Scatter Plot"
    assert widget.state.properties["x_data"] == []
    assert widget.state.properties["y_data"] == []
    assert widget.state.properties["scatter_label"] == "Points"


def test_scatter_plot_widget_creation_with_data():
    """Test ScatterPlotWidget creation with data."""
    x_data = [1.0, 2.0, 3.0]
    y_data = [4.0, 5.0, 6.0]
    widget = ScatterPlotWidget(
        "scatter-2",
        title="My Scatter",
        x_data=x_data,
        y_data=y_data,
        scatter_label="Samples",
    )

    assert widget.state.properties["x_data"] == x_data
    assert widget.state.properties["y_data"] == y_data
    assert widget.state.properties["scatter_label"] == "Samples"


def test_scatter_plot_widget_serialization():
    """Test ScatterPlotWidget serialization."""
    widget = ScatterPlotWidget("scatter-3", x_data=[0.0], y_data=[1.0])

    data = widget.serialize()

    assert data["widget_id"] == "scatter-3"
    assert data["widget_type"] == "ScatterPlotWidget"


# ==============================================================================
# HistogramWidget Tests
# ==============================================================================


def test_histogram_widget_creation_defaults():
    """Test HistogramWidget creation with default values."""
    widget = HistogramWidget("hist-1")

    assert widget.widget_id == "hist-1"
    assert widget.state.widget_type == "HistogramWidget"
    assert widget.state.properties["title"] == "Histogram"
    assert widget.state.properties["values"] == []
    assert widget.state.properties["bins"] == 10
    assert widget.state.properties["histogram_label"] == "Distribution"


def test_histogram_widget_creation_with_data():
    """Test HistogramWidget creation with data."""
    values = [1.0, 2.0, 2.0, 3.0, 3.0, 3.0]
    widget = HistogramWidget("hist-2", title="Data Dist", values=values, bins=5)

    assert widget.state.properties["values"] == values
    assert widget.state.properties["bins"] == 5


def test_histogram_widget_serialization():
    """Test HistogramWidget serialization."""
    widget = HistogramWidget("hist-3", values=[1.0, 2.0, 3.0], bins=3)

    data = widget.serialize()

    assert data["widget_id"] == "hist-3"
    assert data["widget_type"] == "HistogramWidget"
    assert data["properties"]["bins"] == 3


# ==============================================================================
# HeatmapWidget Tests
# ==============================================================================


def test_heatmap_widget_creation_defaults():
    """Test HeatmapWidget creation with default values."""
    widget = HeatmapWidget("heat-1")

    assert widget.widget_id == "heat-1"
    assert widget.state.widget_type == "HeatmapWidget"
    assert widget.state.properties["title"] == "Heatmap"
    assert widget.state.properties["values"] == []
    assert widget.state.properties["heatmap_label"] == "Heatmap"
    assert widget.state.properties["scale_min"] == 0.0
    assert widget.state.properties["scale_max"] == 1.0


def test_heatmap_widget_creation_with_data():
    """Test HeatmapWidget creation with 2D data."""
    values = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    widget = HeatmapWidget(
        "heat-2",
        title="Temperature Map",
        values=values,
        scale_min=-1.0,
        scale_max=1.0,
    )

    assert widget.state.properties["values"] == values
    assert widget.state.properties["scale_min"] == -1.0
    assert widget.state.properties["scale_max"] == 1.0


def test_heatmap_widget_serialization():
    """Test HeatmapWidget serialization."""
    values = [[0.5, 0.8], [0.2, 0.9]]
    widget = HeatmapWidget("heat-3", values=values)

    data = widget.serialize()

    assert data["widget_id"] == "heat-3"
    assert data["widget_type"] == "HeatmapWidget"
    assert data["properties"]["values"] == values


# ==============================================================================
# PieChartWidget Tests
# ==============================================================================


def test_pie_chart_widget_creation_defaults():
    """Test PieChartWidget creation with default values."""
    widget = PieChartWidget("pie-1")

    assert widget.widget_id == "pie-1"
    assert widget.state.widget_type == "PieChartWidget"
    assert widget.state.properties["values"] == []
    assert widget.state.properties["labels"] == []
    assert widget.state.properties["center"] == (0.5, 0.5)
    assert widget.state.properties["radius"] == 0.4


def test_pie_chart_widget_creation_with_data():
    """Test PieChartWidget creation with data."""
    values = [30.0, 45.0, 25.0]
    labels = ["A", "B", "C"]
    widget = PieChartWidget(
        "pie-2",
        values=values,
        labels=labels,
        center=(0.4, 0.6),
        radius=0.35,
    )

    assert widget.state.properties["values"] == values
    assert widget.state.properties["labels"] == labels
    assert widget.state.properties["center"] == (0.4, 0.6)
    assert widget.state.properties["radius"] == 0.35


def test_pie_chart_widget_serialization():
    """Test PieChartWidget serialization."""
    widget = PieChartWidget("pie-3", values=[50.0, 50.0], labels=["Yes", "No"])

    data = widget.serialize()

    assert data["widget_id"] == "pie-3"
    assert data["widget_type"] == "PieChartWidget"
    assert data["properties"]["values"] == [50.0, 50.0]
    assert data["properties"]["labels"] == ["Yes", "No"]


# ==============================================================================
# RealtimePlotWidget Tests
# ==============================================================================


def test_realtime_plot_widget_creation_defaults():
    """Test RealtimePlotWidget creation with default values."""
    widget = RealtimePlotWidget("rt-1")

    assert widget.widget_id == "rt-1"
    assert widget.state.widget_type == "RealtimePlotWidget"
    assert widget.state.properties["title"] == "Realtime Plot"
    assert widget.state.properties["data"] == []
    assert widget.state.properties["max_points"] == 1000
    assert widget.state.properties["line_label"] == "Signal"


def test_realtime_plot_widget_add_point():
    """Test RealtimePlotWidget add_point method."""
    widget = RealtimePlotWidget("rt-2", max_points=5)

    widget.add_point(1.0)
    widget.add_point(2.0)
    widget.add_point(3.0)

    assert widget.state.properties["data"] == [1.0, 2.0, 3.0]


def test_realtime_plot_widget_max_points_enforcement():
    """Test RealtimePlotWidget enforces max_points limit."""
    widget = RealtimePlotWidget("rt-3", max_points=3)

    for i in range(5):
        widget.add_point(float(i))

    data = widget.state.properties["data"]
    assert len(data) == 3
    # Should keep the most recent points
    assert data == [2.0, 3.0, 4.0]


def test_realtime_plot_widget_serialization():
    """Test RealtimePlotWidget serialization."""
    widget = RealtimePlotWidget("rt-4", max_points=100)

    data = widget.serialize()

    assert data["widget_id"] == "rt-4"
    assert data["widget_type"] == "RealtimePlotWidget"
    assert data["properties"]["max_points"] == 100


# ==============================================================================
# ErrorBarsWidget Tests
# ==============================================================================


def test_error_bars_widget_creation_defaults():
    """Test ErrorBarsWidget creation with default values."""
    widget = ErrorBarsWidget("err-1")

    assert widget.widget_id == "err-1"
    assert widget.state.widget_type == "ErrorBarsWidget"
    assert widget.state.properties["title"] == "Error Bars"
    assert widget.state.properties["x_data"] == []
    assert widget.state.properties["y_data"] == []
    assert widget.state.properties["y_errors"] == []
    assert widget.state.properties["error_label"] == "Data"


def test_error_bars_widget_creation_with_data():
    """Test ErrorBarsWidget creation with data."""
    x_data = [1.0, 2.0, 3.0]
    y_data = [2.0, 4.0, 3.0]
    y_errors = [0.1, 0.2, 0.15]
    widget = ErrorBarsWidget(
        "err-2",
        title="Measurements",
        x_data=x_data,
        y_data=y_data,
        y_errors=y_errors,
        error_label="Exp A",
    )

    assert widget.state.properties["x_data"] == x_data
    assert widget.state.properties["y_data"] == y_data
    assert widget.state.properties["y_errors"] == y_errors
    assert widget.state.properties["error_label"] == "Exp A"


def test_error_bars_widget_serialization():
    """Test ErrorBarsWidget serialization."""
    widget = ErrorBarsWidget(
        "err-3",
        x_data=[1.0],
        y_data=[2.0],
        y_errors=[0.1],
    )

    data = widget.serialize()

    assert data["widget_id"] == "err-3"
    assert data["widget_type"] == "ErrorBarsWidget"
    assert data["properties"]["x_data"] == [1.0]


# ==============================================================================
# Module import tests
# ==============================================================================


def test_plotting_widgets_importable_from_package():
    """Test that all plotting widgets are importable from the widgets package."""
    from champi_imgui.widgets import (
        BarChartWidget,
        ErrorBarsWidget,
        HeatmapWidget,
        HistogramWidget,
        LineChartWidget,
        PieChartWidget,
        RealtimePlotWidget,
        ScatterPlotWidget,
    )

    assert LineChartWidget is not None
    assert BarChartWidget is not None
    assert ScatterPlotWidget is not None
    assert HistogramWidget is not None
    assert HeatmapWidget is not None
    assert PieChartWidget is not None
    assert RealtimePlotWidget is not None
    assert ErrorBarsWidget is not None
