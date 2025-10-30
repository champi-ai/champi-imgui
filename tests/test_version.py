"""Test package version."""

from champi_imgui import __version__


def test_version():
    """Test that version is set."""
    assert __version__ == "0.0.1"
