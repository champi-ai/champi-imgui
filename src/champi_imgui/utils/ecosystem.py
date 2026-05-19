"""Ecosystem availability guard.

HAS_ECOSYSTEM is True when both champi-signals and champi-ipc are installed.
Install them with: uv pip install champi-imgui[ecosystem]
"""

try:
    import champi_ipc  # noqa: F401
    import champi_signals  # noqa: F401

    HAS_ECOSYSTEM = True
except ImportError:
    HAS_ECOSYSTEM = False
