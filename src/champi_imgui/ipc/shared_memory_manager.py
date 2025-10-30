"""Shared memory manager for IPC between MCP server and Canvas render process.

Adapted from mcp_champi/ipc_svc/ shared memory pattern.
"""

import struct
import time
from multiprocessing import shared_memory
from typing import Any

from loguru import logger

from champi_imgui.ipc.command_types import CommandType
from champi_imgui.ipc.structs import (
    CommandData,
    pack_ack,
    pack_command,
    unpack_ack,
    unpack_command,
)

# Maximum size for command region (use largest struct)
MAX_COMMAND_SIZE = 512


class SharedMemoryManager:
    """Manages shared memory regions for Canvas IPC.

    Canvas process creates memory regions (producer).
    MCP server attaches to existing regions (consumer).

    Memory layout per canvas:
    - Command region: MCP server writes commands, Canvas reads
    - ACK region: Canvas writes acknowledgments, MCP server reads
    """

    def __init__(self, name_prefix: str = "canvas"):
        """Initialize shared memory manager.

        Args:
            name_prefix: Prefix for shared memory region names
                        (e.g., "canvas_main" creates "canvas_main_cmd")
        """
        self.name_prefix = name_prefix
        self.cmd_region: shared_memory.SharedMemory | None = None
        self.ack_region: shared_memory.SharedMemory | None = None
        self.is_creator = False
        self._seq_num = 0

    def create_regions(self) -> None:
        """Create shared memory regions (Canvas process only).

        Creates two regions:
        - Command region: For commands from MCP server
        - ACK region: For acknowledgments from Canvas
        """
        self.is_creator = True

        # Create command region
        cmd_name = f"{self.name_prefix}_cmd"
        try:
            self.cmd_region = shared_memory.SharedMemory(
                name=cmd_name, create=True, size=MAX_COMMAND_SIZE
            )
            # Initialize with zeros
            self.cmd_region.buf[:] = bytes(MAX_COMMAND_SIZE)
            logger.debug(f"Created command region: {cmd_name}")
        except FileExistsError:
            # Region already exists, attach to it
            logger.warning(
                f"Command region {cmd_name} already exists, attaching instead"
            )
            self.cmd_region = shared_memory.SharedMemory(name=cmd_name)

        # Create ACK region
        ack_name = f"{self.name_prefix}_ack"
        try:
            self.ack_region = shared_memory.SharedMemory(
                name=ack_name,
                create=True,
                size=8,  # Just sequence number
            )
            self.ack_region.buf[:] = bytes(8)
            logger.debug(f"Created ACK region: {ack_name}")
        except FileExistsError:
            logger.warning(f"ACK region {ack_name} already exists, attaching instead")
            self.ack_region = shared_memory.SharedMemory(name=ack_name)

    def attach_regions(self) -> None:
        """Attach to existing shared memory regions (MCP server only).

        Attaches to regions created by Canvas process.
        """
        self.is_creator = False

        # Attach to command region
        cmd_name = f"{self.name_prefix}_cmd"
        self.cmd_region = shared_memory.SharedMemory(name=cmd_name)
        logger.debug(f"Attached to command region: {cmd_name}")

        # Attach to ACK region
        ack_name = f"{self.name_prefix}_ack"
        self.ack_region = shared_memory.SharedMemory(name=ack_name)
        logger.debug(f"Attached to ACK region: {ack_name}")

    def write_command(self, command_type: CommandType, **kwargs: Any) -> int:
        """Write command to shared memory (MCP server side).

        Args:
            command_type: Type of command to write
            **kwargs: Command-specific data

        Returns:
            Sequence number of written command
        """
        if self.cmd_region is None:
            msg = "Command region not initialized. Call attach_regions() first."
            raise RuntimeError(msg)

        self._seq_num += 1
        seq_num = self._seq_num

        # Pack command
        command_bytes = pack_command(command_type, seq_num, **kwargs)

        # Write to shared memory
        size = len(command_bytes)
        self.cmd_region.buf[:size] = command_bytes

        logger.debug(f"Wrote command {command_type.name} (seq={seq_num})")
        return seq_num

    def read_command(self, timeout: float = 0.0) -> CommandData | None:
        """Read command from shared memory (Canvas side).

        Args:
            timeout: Maximum time to wait for command (0 = non-blocking)

        Returns:
            CommandData if available, None otherwise
        """
        if self.cmd_region is None:
            msg = "Command region not initialized. Call create_regions() first."
            raise RuntimeError(msg)

        start_time = time.time()

        while True:
            # Read from shared memory
            data = bytes(self.cmd_region.buf[:MAX_COMMAND_SIZE])

            # Check if data is all zeros (no command)
            if data == bytes(MAX_COMMAND_SIZE):
                if timeout == 0:
                    return None
                if time.time() - start_time >= timeout:
                    return None
                time.sleep(0.001)  # Short sleep to avoid busy-wait
                continue

            # Unpack command
            try:
                command_data = unpack_command(data)
                # Clear the command region after reading
                self.cmd_region.buf[:] = bytes(MAX_COMMAND_SIZE)
                logger.debug(
                    f"Read command {command_data.command_type.name} (seq={command_data.seq_num})"
                )
                return command_data
            except (ValueError, struct.error) as e:
                logger.error(f"Error unpacking command: {e}")
                # Clear invalid data
                self.cmd_region.buf[:] = bytes(MAX_COMMAND_SIZE)
                return None

    def write_ack(self, seq_num: int) -> None:
        """Write acknowledgment to shared memory (Canvas side).

        Args:
            seq_num: Sequence number to acknowledge
        """
        if self.ack_region is None:
            msg = "ACK region not initialized. Call create_regions() first."
            raise RuntimeError(msg)

        ack_bytes = pack_ack(seq_num)
        self.ack_region.buf[:8] = ack_bytes
        logger.debug(f"Wrote ACK for seq={seq_num}")

    def read_ack(self, timeout: float = 1.0) -> int | None:
        """Read acknowledgment from shared memory (MCP server side).

        Args:
            timeout: Maximum time to wait for ACK

        Returns:
            Sequence number if ACK received, None otherwise
        """
        if self.ack_region is None:
            msg = "ACK region not initialized. Call attach_regions() first."
            raise RuntimeError(msg)

        start_time = time.time()

        while True:
            data = bytes(self.ack_region.buf[:8])

            # Check if data is all zeros (no ACK)
            if data == bytes(8):
                if time.time() - start_time >= timeout:
                    return None
                time.sleep(0.001)
                continue

            # Unpack ACK
            try:
                seq_num = unpack_ack(data)
                # Clear ACK after reading
                self.ack_region.buf[:] = bytes(8)
                logger.debug(f"Read ACK for seq={seq_num}")
                return seq_num
            except struct.error as e:
                logger.error(f"Error unpacking ACK: {e}")
                return None

    def cleanup(self) -> None:
        """Close and optionally unlink shared memory regions."""
        if self.cmd_region is not None:
            self.cmd_region.close()
            if self.is_creator:
                try:
                    self.cmd_region.unlink()
                    logger.debug(f"Unlinked command region: {self.name_prefix}_cmd")
                except FileNotFoundError:
                    pass

        if self.ack_region is not None:
            self.ack_region.close()
            if self.is_creator:
                try:
                    self.ack_region.unlink()
                    logger.debug(f"Unlinked ACK region: {self.name_prefix}_ack")
                except FileNotFoundError:
                    pass

    def __enter__(self) -> "SharedMemoryManager":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with cleanup."""
        self.cleanup()
