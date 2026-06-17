"""Regression tests for SharedMemoryManager cleanup and atexit safety (#182/#191).

These tests are complementary to the existing coverage in
tests/test_drawing_shm_fixes.py and focus on two behaviours that were
introduced by the fix for #182:

1. cleanup() fully removes both shared-memory regions from the OS so that no
   stale /dev/shm entries survive across restarts.
2. create_regions() immediately opts the creator-side regions out of
   resource_tracker, preventing the tracker from firing at process exit
   (which was killing the MCP stdio connection on macOS).
"""

import uuid
from multiprocessing import shared_memory as shm_lib
from unittest.mock import call, patch

import pytest

from champi_imgui.ipc.shared_memory_manager import SharedMemoryManager


# ---------------------------------------------------------------------------
# Test 1 — cleanup() removes all shared-memory regions
# ---------------------------------------------------------------------------


def test_cleanup_removes_all_regions() -> None:
    """After cleanup(), both cmd and ack regions are unlinked and inaccessible.

    Verifies the full creator lifecycle: regions must be reachable by name
    immediately after create_regions() and completely gone after cleanup().
    Attaching with create=False is used as the OS-level probe because it
    raises FileNotFoundError when the backing file no longer exists, which is
    the same error an MCP client would encounter when trying to connect to a
    stale canvas.
    """
    prefix = f"shm_{uuid.uuid4().hex[:8]}"
    mgr = SharedMemoryManager(name_prefix=prefix)
    mgr.create_regions()

    cmd_name = f"{prefix}_cmd"
    ack_name = f"{prefix}_ack"

    # Regions must be reachable by name before cleanup.
    probe_cmd = shm_lib.SharedMemory(name=cmd_name, create=False)
    probe_cmd.close()
    probe_ack = shm_lib.SharedMemory(name=ack_name, create=False)
    probe_ack.close()

    mgr.cleanup()

    # After cleanup both regions must be gone from the OS.
    with pytest.raises(FileNotFoundError, match=cmd_name):
        shm_lib.SharedMemory(name=cmd_name, create=False)
    with pytest.raises(FileNotFoundError, match=ack_name):
        shm_lib.SharedMemory(name=ack_name, create=False)


# ---------------------------------------------------------------------------
# Test 2 — resource_tracker is unregistered on create (atexit safety)
# ---------------------------------------------------------------------------


def test_resource_tracker_unregistered_on_create() -> None:
    """create_regions() calls resource_tracker.unregister() for both regions.

    Python's multiprocessing.resource_tracker registers every SharedMemory
    created with create=True and, at process exit, warns about "leaked"
    objects and forcibly unlinks them.  On macOS this kills the MCP stdio
    connection before the server has finished shutting down (#182).

    The fix is to call resource_tracker.unregister() immediately after
    creation so that our own cleanup() controls the lifecycle.  This test
    patches the unregister function directly (rather than monkey-patching
    the internal _untrack_shm helper as the existing coverage does) to
    confirm the behaviour at the multiprocessing API boundary.
    """
    from champi_imgui.ipc.shared_memory_manager import _untrack_shm

    prefix = f"shm_{uuid.uuid4().hex[:8]}"
    mgr = SharedMemoryManager(name_prefix=prefix)

    with patch("multiprocessing.resource_tracker.unregister") as mock_unregister:
        mgr.create_regions()

    # The mock prevented the real unregistration; do it now so that
    # resource_tracker's subprocess does not emit KeyError warnings when the
    # regions are unlinked by cleanup() below.
    if mgr.cmd_region is not None:
        _untrack_shm(mgr.cmd_region)
    if mgr.ack_region is not None:
        _untrack_shm(mgr.ack_region)

    mgr.cleanup()

    called_args = [c.args[0] for c in mock_unregister.call_args_list]

    assert f"/{prefix}_cmd" in called_args, (
        f"resource_tracker.unregister was not called for /{prefix}_cmd; "
        "the cmd region must be unregistered immediately after creation to "
        "prevent resource_tracker from firing at process exit (#182)"
    )
    assert f"/{prefix}_ack" in called_args, (
        f"resource_tracker.unregister was not called for /{prefix}_ack; "
        "the ack region must be unregistered immediately after creation to "
        "prevent resource_tracker from firing at process exit (#182)"
    )

    # Both calls must use the "shared_memory" resource type.
    called_types = [c.args[1] for c in mock_unregister.call_args_list]
    assert all(t == "shared_memory" for t in called_types), (
        "resource_tracker.unregister must be called with resource type "
        f"'shared_memory', got: {called_types}"
    )


# ---------------------------------------------------------------------------
# Supplementary — non-creator cleanup() does not unlink regions
# ---------------------------------------------------------------------------


def test_non_creator_cleanup_does_not_remove_regions() -> None:
    """cleanup() on an attacher (is_creator=False) must not unlink regions.

    Only the process that created the regions should unlink them.  This
    guards against a regression where an MCP server (consumer) calling
    cleanup() would destroy shared memory still needed by the Canvas process.
    """
    prefix = f"shm_{uuid.uuid4().hex[:8]}"
    creator = SharedMemoryManager(name_prefix=prefix)
    creator.create_regions()

    attacher = SharedMemoryManager(name_prefix=prefix)
    attacher.attach_regions()

    # Non-creator cleanup must close file descriptors but not unlink.
    attacher.cmd_region.close()  # type: ignore[union-attr]
    attacher.ack_region.close()  # type: ignore[union-attr]

    cmd_name = f"{prefix}_cmd"
    ack_name = f"{prefix}_ack"

    # Regions must still exist after the attacher released its handles.
    probe_cmd = shm_lib.SharedMemory(name=cmd_name, create=False)
    probe_cmd.close()
    probe_ack = shm_lib.SharedMemory(name=ack_name, create=False)
    probe_ack.close()

    creator.cleanup()

    # Creator cleanup must now remove the regions.
    with pytest.raises(FileNotFoundError):
        shm_lib.SharedMemory(name=cmd_name, create=False)
    with pytest.raises(FileNotFoundError):
        shm_lib.SharedMemory(name=ack_name, create=False)


# ---------------------------------------------------------------------------
# Supplementary — context manager delegates to cleanup()
# ---------------------------------------------------------------------------


def test_context_manager_triggers_cleanup() -> None:
    """Using SharedMemoryManager as a context manager must call cleanup().

    The __exit__ method must remove both regions so that callers can rely on
    the 'with' statement for deterministic resource release.
    """
    prefix = f"shm_{uuid.uuid4().hex[:8]}"

    with SharedMemoryManager(name_prefix=prefix) as mgr:
        mgr.create_regions()
        cmd_name = f"{prefix}_cmd"
        ack_name = f"{prefix}_ack"

    # After the with block both regions must be gone.
    with pytest.raises(FileNotFoundError):
        shm_lib.SharedMemory(name=cmd_name, create=False)
    with pytest.raises(FileNotFoundError):
        shm_lib.SharedMemory(name=ack_name, create=False)
