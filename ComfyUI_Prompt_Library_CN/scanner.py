"""Directory scanner that produces dropdown entries for Prompt Library files (V2)."""

import os
from pathlib import Path
from typing import List, Tuple


def scan(base_dir: str | Path) -> List[Tuple[str, str]]:
    """Recursively scan *base_dir* for ``.txt`` files.

    Returns:
        A list of ``(relative_path, absolute_path)`` tuples, sorted
        alphabetically by relative path.  Relative paths use forward
        slashes so they display cleanly in ComfyUI dropdowns.
    """
    base = Path(base_dir)
    entries: List[Tuple[str, str]] = []

    if not base.is_dir():
        return entries

    for child in sorted(base.rglob("*.txt")):
        if child.is_file():
            rel = str(child.relative_to(base).as_posix())
            entries.append((rel, str(child.resolve())))

    return entries


def ensure_library_dir(base_dir: str | Path) -> None:
    """Create the library directory (and parents) if it does not exist."""
    Path(base_dir).mkdir(parents=True, exist_ok=True)
