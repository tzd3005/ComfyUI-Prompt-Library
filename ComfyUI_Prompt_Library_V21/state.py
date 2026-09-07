"""Per-file persistent state management with atomic writes (V2).

与 v1 的状态文件格式保持一致（同一目录下 ``.state.json``），
方便在同一批 txt 上无缝升级，历史读取进度不丢失。
"""

import json
import os
import tempfile
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List


@dataclass
class PromptState:
    """Persistent reading progress for a single prompt library file."""

    mode: str = "random"
    index: int = 0
    pool: List[int] = field(default_factory=list)  # remaining indices for NeverRepeat
    # V2 新增：最近一次实际命中的行号（1-based），用于诊断/展示
    last_line: int = 0


def _state_path(txt_path: str | Path) -> str:
    p = Path(txt_path)
    return str(p.with_name(p.stem + ".state.json"))


def load(txt_path: str | Path) -> PromptState:
    """Load the state file adjacent to *txt_path*. Returns defaults on any failure."""
    sp = _state_path(txt_path)
    try:
        with open(sp, encoding="utf-8") as f:
            data = json.load(f)
        return PromptState(
            mode=data.get("mode", "random"),
            index=data.get("index", 0),
            pool=data.get("pool", []),
            last_line=data.get("last_line", 0),
        )
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return PromptState()


def save(txt_path: str | Path, state: PromptState) -> None:
    """Atomically write *state* to the adjacent state file."""
    sp = _state_path(txt_path)
    os.makedirs(os.path.dirname(sp) or ".", exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(sp) or ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(asdict(state), f, ensure_ascii=False, separators=(",", ":"))
        os.replace(tmp, sp)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
