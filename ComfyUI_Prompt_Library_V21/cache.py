"""Thread-safe file cache with automatic reload on change (V2)."""

import os
import threading
from pathlib import Path
from typing import Dict, List

from .utils import load_lines


class CacheEntry:
    __slots__ = ("lines", "mtime", "size")

    def __init__(self, lines, mtime, size):
        self.lines = lines
        self.mtime = mtime
        self.size = size


class PromptCache:
    """A thread-safe cache for prompt library text files.

    Each file is cached by its absolute path. The cache validates file
    size and modification time before returning cached content.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._entries: Dict[str, CacheEntry] = {}

    def get(self, filepath, skip_empty=True, skip_comment=True):
        path = os.fspath(filepath)
        with self._lock:
            entry = self._entries.get(path)
            current_stat = os.stat(path)
            current_size = current_stat.st_size
            current_mtime = current_stat.st_mtime

            if entry is None or entry.size != current_size or entry.mtime != current_mtime:
                lines = load_lines(path, skip_empty=skip_empty, skip_comment=skip_comment)
                self._entries[path] = CacheEntry(lines, current_mtime, current_size)
                return lines

            return entry.lines

    def invalidate(self, filepath):
        path = os.fspath(filepath)
        with self._lock:
            self._entries.pop(path, None)

    def clear(self):
        with self._lock:
            self._entries.clear()


# Module-level singleton — shared by all node instances.
GLOBAL_CACHE = PromptCache()
