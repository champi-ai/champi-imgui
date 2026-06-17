#!/usr/bin/env python3
"""SharedMemory lifecycle debug script — investigation for issue #182.

Demonstrates the correct create → use → cleanup lifecycle of SharedMemory
regions used by champi-imgui IPC, and documents the macOS-specific failure
mode that was fixed in PR #193.

Usage:
    uv run python scripts/debug_shm_182.py

Exit codes:
    0 - All lifecycle assertions passed (expected on Linux)
    1 - An assertion or unexpected error occurred

---
LINUX vs macOS PLATFORM DIFFERENCE
------------------------------------
On Linux, POSIX shared memory lives under /dev/shm/ (a tmpfs).  Python's
multiprocessing.resource_tracker subprocess watches for SharedMemory objects
created with create=True and unlinks them on process exit *only* when it
believes they were leaked (i.e. not explicitly closed/unlinked by the
application).  The tracker emits a ResourceWarning but does NOT forcibly
kill the process, so MCP stdio channels survive shutdown.

On macOS (Apple Silicon + Python 3.13), the resource_tracker behaves more
aggressively: it unlinks POSIX shm regions at exit *before* the atexit chain
runs, and it may raise a signal that terminates the process abruptly.  When
champi-imgui ran as an MCP server (communicating over stdio), this caused the
MCP client to see an unexpected EOF — losing the connection and crashing the
session.

---
MACOS FAILURE MODE (pre-fix, issue #182)
------------------------------------------
Symptoms observed (Apple Silicon, Python 3.13, macOS 14 Sonoma):

    ResourceWarning: resource_tracker: /canvas_main_cmd: [Errno 2]
        No such file or directory: '/canvas_main_cmd'
    ResourceWarning: resource_tracker: /canvas_main_ack: [Errno 2]
        No such file or directory: '/canvas_main_ack'

In the worst case the resource_tracker unlinked the shm region *while* the
Canvas render thread still held it open, leading to an EIO or SIGBUS in the
render loop.  The MCP client received an abrupt EOF on stdio and raised:

    mcp.client.exceptions.McpError: Connection closed unexpectedly

The root cause: Python registers every SharedMemory(create=True) with
resource_tracker automatically.  Without the fix the tracker and the
application both tried to unlink the same region — the tracker won the race,
leaving the app cleanup() to raise FileNotFoundError and the region dangling
in an undefined state.

---
THE FIX (PR #193, merged 2026-05-27)
--------------------------------------
`_untrack_shm()` in shared_memory_manager.py calls
`resource_tracker.unregister()` immediately after each
`SharedMemory(create=True)` call.  This transfers ownership of the unlink
lifecycle exclusively to our `cleanup()` method, which is registered via
atexit.  The resource_tracker no longer touches these regions.

---
CI / MACOS AVAILABILITY RISK ITEM
------------------------------------
This environment is Linux only.  The macOS failure mode described above
cannot be reproduced live in this CI/dev environment.  The risk is that a
regression (e.g. removing the _untrack_shm() call) would pass all Linux CI
checks but reintroduce the crash on Apple Silicon.

Mitigation:
  - The _untrack_shm() helper and its call sites are covered by code review
    policy.
  - A macOS GitHub Actions runner should be added to the CI matrix to catch
    resource_tracker regressions automatically.  Track this in a dedicated
    issue if not already done.
"""

import sys
from multiprocessing import shared_memory
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _shm_exists(name: str) -> bool:
    """Return True if a POSIX shm region with *name* is currently accessible."""
    try:
        shm = shared_memory.SharedMemory(name=name)
        shm.close()
        return True
    except FileNotFoundError:
        return False


# ---------------------------------------------------------------------------
# Lifecycle trace
# ---------------------------------------------------------------------------


def run_lifecycle_trace() -> int:
    """Run the full SHM lifecycle and assert each step.

    Returns 0 on success, 1 on failure.
    """
    print("=== SharedMemory lifecycle trace (issue #182) ===\n")

    # Import here so any ImportError surfaces clearly.
    from champi_imgui.ipc.shared_memory_manager import SharedMemoryManager

    prefix = "debug182_test"
    cmd_name = f"{prefix}_cmd"
    ack_name = f"{prefix}_ack"

    # ------------------------------------------------------------------
    # STEP 1: Ensure regions do NOT exist before the test
    # ------------------------------------------------------------------
    print("[1] Pre-condition: regions must not exist before creation")
    for name in (cmd_name, ack_name):
        if _shm_exists(name):
            # Stale region from a previous crashed run — clean it up.
            print(f"    WARNING: stale region /{name} found, removing it")
            stale = shared_memory.SharedMemory(name=name)
            stale.close()
            stale.unlink()
    assert not _shm_exists(cmd_name), f"Stale cmd region /{cmd_name} not cleaned up"
    assert not _shm_exists(ack_name), f"Stale ack region /{ack_name} not cleaned up"
    print("    OK: no pre-existing regions\n")

    mgr = SharedMemoryManager(name_prefix=prefix)
    try:
        # ------------------------------------------------------------------
        # STEP 2: Create regions and verify resource_tracker.unregister is called
        # ------------------------------------------------------------------
        print("[2] create_regions() — regions created, resource_tracker opted out (fix)")

        # Patch multiprocessing.resource_tracker.unregister to spy on calls.
        # We patch the module-level function that _untrack_shm() reaches through:
        #   from multiprocessing import resource_tracker
        #   resource_tracker.unregister(...)
        with patch(
            "multiprocessing.resource_tracker.unregister",
            wraps=lambda name, rtype: None,
        ) as mock_unregister:
            mgr.create_regions()
            unregister_calls = mock_unregister.call_count

        assert mgr.is_creator, "Expected is_creator=True after create_regions()"
        assert mgr.cmd_region is not None, "cmd_region is None after create_regions()"
        assert mgr.ack_region is not None, "ack_region is None after create_regions()"
        print(f"    OK: cmd_region  = /{mgr.cmd_region.name}")
        print(f"    OK: ack_region  = /{mgr.ack_region.name}")

        assert unregister_calls >= 2, (
            f"resource_tracker.unregister() was called {unregister_calls} time(s); "
            "expected at least 2 (once per region) — _untrack_shm() may be missing"
        )
        print(
            f"    OK: resource_tracker.unregister() called {unregister_calls}x "
            "(once per created region)"
        )
        print(
            "    -> On macOS, this prevents the aggressive unlink-at-exit behaviour\n"
            "       that caused the MCP stdio crash described in issue #182\n"
        )

        # ------------------------------------------------------------------
        # STEP 3: Verify regions are visible in the OS
        # ------------------------------------------------------------------
        print("[3] Regions must be accessible by name in the OS")
        assert _shm_exists(cmd_name), (
            f"cmd region /{cmd_name} not accessible after creation"
        )
        assert _shm_exists(ack_name), (
            f"ack region /{ack_name} not accessible after creation"
        )
        print("    OK: both regions are accessible\n")

        # ------------------------------------------------------------------
        # STEP 4: Verify regions are writable (raw buffer test)
        # ------------------------------------------------------------------
        print("[4] Verify cmd_region and ack_region buffers are writable")
        assert mgr.cmd_region is not None
        assert mgr.ack_region is not None

        # Write a recognisable sentinel into the cmd region and read it back.
        sentinel = b"\xde\xad\xbe\xef" + b"\x00" * (mgr.cmd_region.size - 4)
        mgr.cmd_region.buf[: mgr.cmd_region.size] = sentinel
        readback = bytes(mgr.cmd_region.buf[: mgr.cmd_region.size])
        assert readback == sentinel, "cmd_region buffer round-trip mismatch"
        # Reset to zeros (as create_regions() leaves it)
        mgr.cmd_region.buf[: mgr.cmd_region.size] = bytes(mgr.cmd_region.size)
        print("    OK: cmd_region buffer write/read round-trip passed")

        ack_sentinel = b"\xca\xfe\xba\xbe\x00\x00\x00\x00"
        mgr.ack_region.buf[:8] = ack_sentinel
        ack_readback = bytes(mgr.ack_region.buf[:8])
        assert ack_readback == ack_sentinel, "ack_region buffer round-trip mismatch"
        mgr.ack_region.buf[:8] = bytes(8)
        print("    OK: ack_region buffer write/read round-trip passed\n")

    finally:
        # Always clean up to prevent stale regions and resource_tracker warnings
        mgr.cleanup()

    # ------------------------------------------------------------------
    # STEP 5: Verify cleanup removed the regions
    # ------------------------------------------------------------------
    print("[5] cleanup() — regions are closed and unlinked by the application")
    assert not _shm_exists(cmd_name), (
        f"cmd region /{cmd_name} still accessible after cleanup()"
    )
    assert not _shm_exists(ack_name), (
        f"ack region /{ack_name} still accessible after cleanup()"
    )
    print("    OK: both regions are gone after cleanup()\n")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("=== All lifecycle assertions passed ===")
    print()
    print("Lifecycle summary:")
    print("  create_regions()          -> regions appear in OS, resource_tracker opted out")
    print("  buf write/read            -> raw buffer round-trip works correctly")
    print("  cleanup()                 -> regions unlinked by application, not tracker")
    print()
    print("macOS risk note:")
    print("  This trace ran on Linux.  The macOS-specific resource_tracker crash")
    print("  (issue #182) cannot be reproduced live in this environment.  A macOS")
    print("  GitHub Actions runner should be added to CI to catch regressions.")

    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    """Run the SHM lifecycle trace and return an exit code."""
    try:
        return run_lifecycle_trace()
    except AssertionError as exc:
        print(f"\n[FAIL] Assertion failed: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"\n[ERROR] Unexpected exception: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
