"""Prompt Library V2 nodes — Loader (with line metadata) + Preview display node."""

import os
import random
import time
from pathlib import Path
from typing import List, Tuple, Optional

from .cache import GLOBAL_CACHE
from .scanner import scan as scan_dir, ensure_library_dir
from .state import PromptState, load as load_state, save as save_state

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LIBRARY_DIR_NAME = "prompt_library"

# ---------------------------------------------------------------------------
# File listing (2s refresh)
# ---------------------------------------------------------------------------

_file_list_cache: List[Tuple[str, str]] = []
_file_list_mtime: float = 0.0


def _refresh_file_list() -> List[Tuple[str, str]]:
    global _file_list_cache, _file_list_mtime
    now = time.time()
    if now - _file_list_mtime > 2.0:
        base_dir = os.path.join(_custom_nodes_parent(), LIBRARY_DIR_NAME)
        ensure_library_dir(base_dir)
        _file_list_cache = scan_dir(base_dir)
        _file_list_mtime = now
    return _file_list_cache


def _custom_nodes_parent() -> str:
    return str(Path(__file__).resolve().parent.parent.parent)


# ---------------------------------------------------------------------------
# Selection engine (V2)
# ---------------------------------------------------------------------------


def _advance(
    lines: List[str],
    state: PromptState,
    mode: str,
) -> Tuple[str, int, PromptState]:
    """Pick the next line index per *mode*; return (line, 1-based_idx, new_state).

    Returns a **new** state for mutation; caller persists it.
    """
    total = len(lines)
    if total == 0:
        return "", 0, state

    new_state = PromptState(
        mode=mode,
        index=state.index,
        pool=list(state.pool),
        last_line=state.last_line,
    )

    if mode == "random":
        idx = random.randrange(total)
    elif mode == "sequential":
        idx = new_state.index % total
        new_state.index = (new_state.index + 1) % total
    elif mode == "neverrepeat":
        new_state.pool = [i for i in new_state.pool if i < total]
        if not new_state.pool:
            new_state.pool = list(range(total))
            random.shuffle(new_state.pool)
        idx = new_state.pool.pop(0)
    else:
        idx = 0

    new_state.last_line = idx + 1
    return lines[idx], idx + 1, new_state


# ---------------------------------------------------------------------------
# V2 Loader node
# ---------------------------------------------------------------------------

class PromptLibraryLoaderV2:
    """Load prompts from text files, exposing the selected line + metadata."""

    @classmethod
    def INPUT_TYPES(cls):
        files = _refresh_file_list()
        choices = [rel for rel, _ in files]
        if not choices:
            choices = ["(no files)"]
        return {
            "required": {
                "prompt_file": (choices, {"default": choices[0]}),
                "mode": (
                    ["random", "sequential", "neverrepeat"],
                    {"default": "random"},
                ),
                "manual_line": ("INT", {"default": 0, "min": 0, "max": 99999}),
                "auto_reload": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "summary")
    FUNCTION = "get_prompt"
    CATEGORY = "Prompt"

    @classmethod
    def IS_CHANGED(cls, **kwargs) -> float:
        # Force re-execution every run so the selection advances.
        return float("nan")

    def get_prompt(
        self,
        prompt_file: str,
        mode: str,
        manual_line: int,
        auto_reload: bool,
    ) -> Tuple[str, str]:
        files = _refresh_file_list()
        abs_path: Optional[str] = None
        for rel, absp in files:
            if rel == prompt_file:
                abs_path = absp
                break

        if abs_path is None or not os.path.isfile(abs_path):
            print(f"[PromptLibraryLoaderV2] Warning: file not found: {prompt_file}")
            return ("", "")

        if auto_reload:
            lines = GLOBAL_CACHE.get(abs_path, skip_empty=True, skip_comment=True)
        else:
            from .utils import load_lines
            lines = load_lines(abs_path, skip_empty=True, skip_comment=True)

        total = len(lines)
        if total == 0:
            return ("", "")

        state = load_state(abs_path)

        if manual_line > 0:
            # ---- 手动指定行：V2 修复割裂 bug ----
            # 1. 解析 1-based 行号（越界则回绕）。
            # 2. 同步更新持久 state，使后续模式正确接续。
            idx = (manual_line - 1) % total
            new_state = PromptState(
                mode=mode,
                index=(idx + 1) % total,   # sequential 从下一行接续
                pool=list(range(total)),   # neverrepeat 重置一个完整洗牌池
                last_line=idx + 1,
            )
            # 保留用户当前 mode 的既有进度：乱序模式保留旧 pool，
            # 但手动跳转后重新洗牌更符合直觉。这里采用“重置”语义。
            save_state(abs_path, new_state)
            return (lines[idx], self._summary(prompt_file, idx + 1, total))

        prompt, line_no, new_state = _advance(lines, state, mode)
        if new_state is not state:
            save_state(abs_path, new_state)
        return (prompt, self._summary(prompt_file, line_no, total))

    @staticmethod
    def _summary(source: str, line_no: int, total: int) -> str:
        """Human-readable one-liner: ``[demo.txt | 3/12]``."""
        return f"[{source} | {line_no}/{total}]"


# ---------------------------------------------------------------------------
# Preview display node (front-end visible panel)
# ---------------------------------------------------------------------------

class PromptPreview:
    """Display the input text on the canvas.

    Written to match AlekPet's confirmed-working ``PreviewTextNode``
    (ExtrasNode): OUTPUT_NODE=True + RETURN_TYPES=(STRING,) and returns
    {"ui": {"string": [text]}, "result": (text,)}.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    OUTPUT_NODE = True
    FUNCTION = "preview_text"
    CATEGORY = "Prompt"

    def preview_text(self, text: str):
        return {
            "ui": {"string": [text]},
            "result": (text,),
        }


# ---------------------------------------------------------------------------
# Registration — V2 node names are distinct from v1 to avoid conflicts
# ---------------------------------------------------------------------------

NODE_CLASS_MAPPINGS = {
    "ComfyUI_Prompt_Library_V2": PromptLibraryLoaderV2,
    "ComfyUI_Prompt_Preview": PromptPreview,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ComfyUI_Prompt_Library_V2": "ComfyUI Prompt Library V2",
    "ComfyUI_Prompt_Preview": "Prompt Preview",
}


# ---------------------------------------------------------------------------
# Registration — V2 node names are distinct from v1 to avoid conflicts
# ---------------------------------------------------------------------------

NODE_CLASS_MAPPINGS = {
    "ComfyUI_Prompt_Library_V2": PromptLibraryLoaderV2,
    "ComfyUI_Prompt_Preview": PromptPreview,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ComfyUI_Prompt_Library_V2": "ComfyUI Prompt Library V2",
    "ComfyUI_Prompt_Preview": "Prompt Preview",
}
