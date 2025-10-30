"""Command types for IPC between MCP server and Canvas render process."""

from enum import IntEnum


class CommandType(IntEnum):
    """Command type identifiers for Canvas IPC.

    These commands are sent from MCP server to Canvas render process
    via shared memory regions.
    """

    # Canvas management
    CREATE_CANVAS = 1  # Initialize new canvas (placeholder, canvas already exists)
    CLEAR_CANVAS = 2  # Clear all widgets from canvas
    UPDATE_STATE = 3  # Update canvas properties (title, size, etc.)
    SHUTDOWN = 4  # Gracefully shutdown canvas

    # Widget operations (placeholders for Stage 6)
    ADD_WIDGET = 10  # Add widget to canvas
    UPDATE_WIDGET = 11  # Update widget properties
    REMOVE_WIDGET = 12  # Remove widget from canvas

    # Response/acknowledgment
    ACK = 99  # Acknowledgment response
