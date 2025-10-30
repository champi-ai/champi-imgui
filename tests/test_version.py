"""Test package version."""

import re

from champi_imgui import __version__


def test_version():
    """Test that version is set and follows semver format."""
    # Check version exists and is not empty
    assert __version__
    assert isinstance(__version__, str)

    # Check version follows semver pattern (major.minor.patch)
    semver_pattern = r"^\d+\.\d+\.\d+$"
    assert re.match(
        semver_pattern, __version__
    ), f"Version '{__version__}' does not match semver format"
