# log_util.py
# Homemade logger. Modernised: context manager, dead DEBUG branch removed, type hints.

import time

LOG_LINES: list[str] = []   # module-level buffer; call flush_log() or reset_log() to clear


def reset_log() -> None:
    """Clear the in-memory log buffer (call at the start of each test run)."""
    LOG_LINES.clear()


def log(message: str) -> None:
    """Append a timestamped entry to the buffer and print it."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    LOG_LINES.append(line)
    print(line)


def flush_log(path: str) -> None:
    """Write buffered log lines to path (append mode) then clear the buffer."""
    with open(path, "a") as f:
        for line in LOG_LINES:
            f.write(line + "\n")
    LOG_LINES.clear()
