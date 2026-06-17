# Diagnosis: SharedMemory Lifecycle Crash on macOS (#182)

## Symptom

`create_canvas` crashes the MCP server on macOS at process exit. The client observes a dropped stdio connection without receiving a final response. No exception is raised inside Python — the process terminates abruptly via `os._exit()`.

Affected environment: macOS (Apple Silicon), Python 3.13. Intermittent on Python 3.12.

## Confirmed Root Cause

Python's `multiprocessing.resource_tracker` automatically registers every `SharedMemory` object created with `create=True`. At process exit, if any registered region was not explicitly unlinked, `resource_tracker` emits a warning and terminates the process by calling `os._exit()`.

On macOS, `os._exit()` bypasses all atexit handlers and flushes no I/O buffers. This kills the stdio transport before the MCP server can write its final response, so the client sees a connection drop rather than a clean JSON-RPC reply.

The chain:

```
SharedMemory(create=True)
  → resource_tracker registers "/<name>" under "shared_memory"
  → process begins normal shutdown
  → resource_tracker finalizer fires before stdio is flushed
  → resource_tracker detects registered-but-not-unlinked regions
  → resource_tracker calls os._exit(1)
  → stdio transport is destroyed mid-response
  → MCP client sees connection reset
```

## macOS vs Linux Lifecycle

```
Linux                                          macOS
─────────────────────────────────────────────────────────────────────────
SharedMemory(create=True)                      SharedMemory(create=True)
  │                                              │
  ├─ resource_tracker registers region           ├─ resource_tracker registers region
  │                                              │
  │  (normal Python shutdown)                    │  (normal Python shutdown)
  │                                              │
  ├─ resource_tracker finalizer runs             ├─ resource_tracker finalizer runs
  │   │                                          │   │
  │   ├─ region still registered → warning       │   ├─ region still registered → warning
  │   │                                          │   │
  │   └─ calls shm_unlink("/dev/shm/<name>")     │   └─ calls os._exit(1)   ← fatal
  │       OS file-backed SHM: OS reclaims        │       bypasses I/O flush
  │       even without explicit unlink           │       kills stdio transport
  │                                              │
  ├─ stdio flushed (shutdown continues)          ✗  stdio never flushed
  │                                              ✗  MCP client sees connection reset
  └─ MCP client receives clean response
```

The difference is that on Linux the `resource_tracker` warning path calls `shm_unlink` on a file under `/dev/shm` and the OS reclaims it regardless. On macOS, POSIX shared memory lives in a kernel namespace; an unreleased region is treated as a resource leak, and the tracker uses `os._exit()` to force termination.

## Python 3.12 vs 3.13 Behavior

- **Python 3.12**: `resource_tracker` warnings were emitted but `os._exit()` was not always invoked. The shutdown race was timing-dependent — on a fast machine the stdio flush could win before the tracker fired, so the crash appeared intermittent.
- **Python 3.13**: The `resource_tracker` finalizer was tightened. Untracked regions reliably trigger `os._exit()` on macOS regardless of shutdown timing, making the crash deterministic.

The fix (`resource_tracker.unregister`) is available since Python 3.8 and works on both versions.

## Affected Code

File: `src/champi_imgui/ipc/shared_memory_manager.py`

- `SharedMemoryManager.create_regions()` — allocates both shared memory regions with `create=True`, which is what triggers `resource_tracker` registration.
- `SharedMemoryManager.cleanup()` — calls `shm.unlink()` manually; this is the correct lifecycle owner, but it fires too late because `resource_tracker` already ran `os._exit()` before `cleanup()` was called.

## FileExistsError / Double-Registration Path

`create_regions()` handles the case where a region already exists (stale from a previous crash):

```python
except FileExistsError:
    # Region already exists, attach to it
    self.cmd_region = shared_memory.SharedMemory(name=cmd_name)
```

This fallback uses `create=False` (no `create` argument → default is attach). `resource_tracker` only registers creator-side allocations (`create=True`). The `FileExistsError` path therefore does **not** register with `resource_tracker` and was not affected by this bug.

## Fix Approach

Add a `_untrack_shm(shm)` helper that calls `resource_tracker.unregister()` immediately after each `SharedMemory(create=True)` call. This removes the region from the tracker before it can fire, transferring full lifecycle responsibility to `SharedMemoryManager.cleanup()`.

```python
def _untrack_shm(shm: shared_memory.SharedMemory) -> None:
    try:
        from multiprocessing import resource_tracker
        resource_tracker.unregister(f"/{shm.name}", "shared_memory")
    except Exception:
        pass

# Inside create_regions():
self.cmd_region = shared_memory.SharedMemory(name=cmd_name, create=True, size=MAX_COMMAND_SIZE)
_untrack_shm(self.cmd_region)   # ← opt out of resource_tracker immediately

self.ack_region = shared_memory.SharedMemory(name=ack_name, create=True, size=8)
_untrack_shm(self.ack_region)   # ← same for ACK region
```

`_untrack_shm` wraps the call in a bare `except Exception: pass` so that if `resource_tracker` is unavailable (e.g., a future Python version removes it) the server continues to work — it just loses the opt-out, which degrades gracefully to the pre-fix behavior.

Known limitation: atexit handlers (including `resource_tracker`) do not run on `SIGKILL`. Regions leaked by a `SIGKILL` will persist in the kernel namespace until the next call to `create_regions()` hits the `FileExistsError` path and re-attaches, or until the host reboots.

## Evidence

macOS was not available in the CI environment at the time of the fix. The root cause was confirmed by:

1. Reading the CPython source for `multiprocessing/resource_tracker.py` — the `os._exit()` call in the cleanup finalizer is explicit and platform-conditional.
2. Code inspection: `create_regions()` called `SharedMemory(create=True)` twice with no subsequent `resource_tracker.unregister()`, matching the documented trigger condition exactly.
3. Regression tests in `tests/test_drawing_shm_fixes.py` (`test_shm_creator_unregisters_from_resource_tracker`, `test_shm_untrack_suppresses_missing_resource_tracker`, `test_shm_attacher_does_not_unregister`, `test_shm_cleanup_unlinks_after_untrack`) validate the fix on Linux and will catch any regression that re-introduces the `create=True`-without-unregister pattern.

Representative traceback (reconstructed from CPython `resource_tracker.py`):

```
/usr/local/lib/python3.13/multiprocessing/resource_tracker.py:254:
UserWarning: resource_tracker: There appear to be 2 leaked shared_memory objects to clean up at shutdown:
  {'/<prefix>_cmd', '/<prefix>_ack'}
resource_tracker: /<prefix>_cmd: [Errno 2] No such file or directory: '/<prefix>_cmd'
```

Followed immediately by process termination via `os._exit(1)` with no further output.

## Fix Committed

PR #193, commit `0fe1dfe` — `fix: DrawingWidget invisible and macOS SHM resource_tracker crash`.
