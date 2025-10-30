"""IPC (Inter-Process Communication) module for Canvas and MCP server."""

from champi_imgui.ipc.command_types import CommandType
from champi_imgui.ipc.shared_memory_manager import SharedMemoryManager
from champi_imgui.ipc.structs import CommandData, pack_command, unpack_command

__all__ = [
    "CommandData",
    "CommandType",
    "SharedMemoryManager",
    "pack_command",
    "unpack_command",
]
