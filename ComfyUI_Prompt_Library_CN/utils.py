"""Utility functions for prompt file reading and parsing (V2)."""

import re
from pathlib import Path
from typing import List

_COMMENT_PATTERN = re.compile(r"^\s*(#|//|;)")


def load_lines(
    filepath: str | Path,
    skip_empty: bool = True,
    skip_comment: bool = True,
) -> List[str]:
    """Read a UTF-8 text file, trim lines, and optionally skip empty/comment lines.

    Args:
        filepath: Path to the text file.
        skip_empty: If True, filter out empty lines.
        skip_comment: If True, filter out comment lines (#, //, ;).

    Returns:
        A list of stripped non-empty (and optionally non-comment) lines.

    Raises:
        UnicodeDecodeError: If the file is not valid UTF-8.
        FileNotFoundError: If the file does not exist.
    """
    with open(filepath, encoding="utf-8-sig", newline="") as f:
        lines = f.readlines()

    result: List[str] = []
    for raw in lines:
        stripped = raw.strip()
        if skip_empty and not stripped:
            continue
        if skip_comment and _COMMENT_PATTERN.match(stripped):
            continue
        result.append(stripped)

    return result
