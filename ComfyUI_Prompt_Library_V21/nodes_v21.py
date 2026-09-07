"""Prompt Library V21 nodes — Loader (with line metadata) + Preview + Text Editor.

V2.1 adds a single-step, chainable *text editor* node on top of the V2 feature
set (Loader + Preview). Node classNames carry the V21 suffix so V2 and V2.1 can
be installed side by side without conflicts.
"""

import os
import random
import re
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
        base_dir = os.path.join(_plugin_dir(), LIBRARY_DIR_NAME)
        ensure_library_dir(base_dir)
        _file_list_cache = scan_dir(base_dir)
        _file_list_mtime = now
    return _file_list_cache


def _plugin_dir() -> str:
    """Return this plugin's own directory.

    V2.1 stores its ``prompt_library`` **inside the plugin folder**, i.e.
    ``<custom_nodes>/ComfyUI_Prompt_Library_V21/prompt_library/``,
    instead of under the ComfyUI root as in V2.
    """
    return str(Path(__file__).resolve().parent)


# ---------------------------------------------------------------------------
# Selection engine
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
# V2.1 Loader node
# ---------------------------------------------------------------------------


class PromptLibraryLoaderV21:
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
            print(f"[PromptLibraryLoaderV21] Warning: file not found: {prompt_file}")
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
            idx = (manual_line - 1) % total
            new_state = PromptState(
                mode=mode,
                index=(idx + 1) % total,
                pool=list(range(total)),
                last_line=idx + 1,
            )
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
# V2.1 Preview display node
# ---------------------------------------------------------------------------


class PromptPreviewV21:
    """Display the input text on the canvas (front-end visible panel)."""

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
# V2.1 Text editor node (single-step, chainable)
# ---------------------------------------------------------------------------


class PromptTextEditorV21:
    """Single-step, chainable text editor for prompts.

    Modes:
      - replace: replace all occurrences of *find* with *replacement*.
      - prepend: insert *replacement* immediately before every *find*.
      - append:  insert *replacement* immediately after every *find*.
      - delete:  remove all occurrences of *find*.

    Set *regex* to True to treat *find* as a regular expression. Chain several
    instances together to build arbitrarily complex edit pipelines.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
                "mode": (
                    ["replace", "prepend", "append", "delete"],
                    {"default": "replace"},
                ),
                "find": ("STRING", {"default": "", "multiline": True}),
                "replacement": ("STRING", {"default": "", "multiline": True}),
                "regex": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("edited",)
    FUNCTION = "edit"
    CATEGORY = "Prompt"

    def edit(
        self,
        text: str,
        mode: str,
        find: str,
        replacement: str,
        regex: bool,
    ) -> Tuple[str]:
        if not find:
            return (text,)

        try:
            if regex:
                _pattern = re.compile(find)
            else:
                _pattern = re.compile(re.escape(find))
        except re.error as exc:
            print(f"[PromptTextEditorV21] Regex error: {exc}")
            return (text,)

        if mode == "replace":
            result = _pattern.sub(lambda m: replacement, text)
        elif mode == "prepend":
            result = _pattern.sub(lambda m: replacement + m.group(0), text)
        elif mode == "append":
            result = _pattern.sub(lambda m: m.group(0) + replacement, text)
        elif mode == "delete":
            result = _pattern.sub("", text)
        else:
            result = text

        return (result,)


# ---------------------------------------------------------------------------
# Registration — V21 classNames are distinct to coexist with V2
# ---------------------------------------------------------------------------

NODE_CLASS_MAPPINGS = {
    "ComfyUI_Prompt_Library_V21": PromptLibraryLoaderV21,
    "ComfyUI_Prompt_Preview_V21": PromptPreviewV21,
    "ComfyUI_Prompt_Text_Editor": PromptTextEditorV21,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ComfyUI_Prompt_Library_V21": "ComfyUI Prompt Library V2.1",
    "ComfyUI_Prompt_Preview_V21": "Prompt Preview V2.1",
    "ComfyUI_Prompt_Text_Editor": "Prompt Text Editor",
}
