"""Prompt Library 中文版 V2.1 节点 — Loader（带行号摘要）+ 自带文本预览 + 文本编辑。

界面与输出文案全部中文化：
  - 参数名、下拉选项标签、分类、打印日志、summary 格式均为中文。
  - mode 内部值保持英文（random/sequential/neverrepeat），逻辑不变。
  - 文本编辑节点可串联（上一个节点的"编辑后文本"接到下一个节点的"文本"）。

节点 className（技术名）:
  - ComfyUI_Prompt_Library_V21_CN : 提示词加载器（中文版 V2.1）
  - ComfyUI_Prompt_Preview_V21_CN : 提示词预览（中文版 V2.1）
  - ComfyUI_Prompt_Text_Editor_CN : 文本编辑（中文版 V2.1）
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
# 常量
# ---------------------------------------------------------------------------

LIBRARY_DIR_NAME = "prompt_library"

# ---------------------------------------------------------------------------
# 文件列表（2 秒刷新）
# ---------------------------------------------------------------------------

_file_list_cache: List[Tuple[str, str]] = []
_file_list_mtime: float = 0.0


def _refresh_file_list() -> List[Tuple[str, str]]:
    global _file_list_cache, _file_list_mtime
    now = time.time()
    if now - _file_list_mtime > 2.0:
        base_dir = os.path.join(_插件目录(), LIBRARY_DIR_NAME)
        ensure_library_dir(base_dir)
        _file_list_cache = scan_dir(base_dir)
        _file_list_mtime = now
    return _file_list_cache


def _插件目录() -> str:
    """返回本插件自身的目录。

    V2.1 将 ``prompt_library`` 放在插件目录内，即
    ``<custom_nodes>/ComfyUI_Prompt_Library_V21_CN/prompt_library/``，
    而不是像 V2 那样放在 ComfyUI 根目录。
    """
    return str(Path(__file__).resolve().parent)


# ---------------------------------------------------------------------------
# 选择引擎
# ---------------------------------------------------------------------------


def _advance(
    lines: List[str],
    state: PromptState,
    mode: str,
) -> Tuple[str, int, PromptState]:
    """按 *mode* 选择下一行；返回 (行内容, 1-based 行号, 新 state)。"""
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
# 中文版 V2.1 加载器
# ---------------------------------------------------------------------------


class PromptLibraryLoaderV21CN:
    """从文本文件加载提示词，并输出行号摘要（中文界面）。"""

    @classmethod
    def INPUT_TYPES(cls):
        files = _refresh_file_list()
        choices = [rel for rel, _ in files]
        if not choices:
            choices = ["(无文件)"]
        return {
            "required": {
                "提示词文件": (choices, {"default": choices[0]}),
                "抽取模式": (
                    ["随机(random)", "顺序(sequential)", "不重复(neverrepeat)"],
                    {"default": "随机(random)"},
                ),
                "手动指定行": ("INT", {"default": 0, "min": 0, "max": 99999}),
                "自动重载文件": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("提示词", "摘要")
    FUNCTION = "获取提示词"
    CATEGORY = "提示词"

    @classmethod
    def IS_CHANGED(cls, **kwargs) -> float:
        # 强制每次执行都重跑，保证推进。
        return float("nan")

    def 获取提示词(
        self,
        提示词文件: str,
        抽取模式: str,
        手动指定行: int,
        自动重载文件: bool,
    ) -> Tuple[str, str]:
        # 模式：中文标签 -> 英文内部值
        mode = 抽取模式.split("(")[1].rstrip(")") if "(" in 抽取模式 else 抽取模式

        files = _refresh_file_list()
        abs_path: Optional[str] = None
        for rel, absp in files:
            if rel == 提示词文件:
                abs_path = absp
                break

        if abs_path is None or not os.path.isfile(abs_path):
            print(f"[提示词库:中文版V2.1] 警告：找不到文件: {提示词文件}")
            return ("", "")

        if 自动重载文件:
            lines = GLOBAL_CACHE.get(abs_path, skip_empty=True, skip_comment=True)
        else:
            from .utils import load_lines
            lines = load_lines(abs_path, skip_empty=True, skip_comment=True)

        total = len(lines)
        if total == 0:
            return ("", "")

        state = load_state(abs_path)

        if 手动指定行 > 0:
            idx = (手动指定行 - 1) % total
            new_state = PromptState(
                mode=mode,
                index=(idx + 1) % total,
                pool=list(range(total)),
                last_line=idx + 1,
            )
            save_state(abs_path, new_state)
            return (lines[idx], self._摘要(提示词文件, idx + 1, total))

        prompt, line_no, new_state = _advance(lines, state, mode)
        if new_state is not state:
            save_state(abs_path, new_state)
        return (prompt, self._摘要(提示词文件, line_no, total))

    @staticmethod
    def _摘要(source: str, line_no: int, total: int) -> str:
        """人类可读摘要：``[demo.txt | 第X/Y行]``。"""
        return f"[{source} | 第{line_no}/{total}行]"


# ---------------------------------------------------------------------------
# 中文版 V2.1 预览节点
# ---------------------------------------------------------------------------


class PromptPreviewV21CN:
    """在画布上显示输入文本（中文版，含只读显示窗口）。"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "文本": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("文本",)
    OUTPUT_NODE = True
    FUNCTION = "显示文本"
    CATEGORY = "提示词"

    def 显示文本(self, 文本: str):
        return {
            "ui": {"string": [文本]},
            "result": (文本,),
        }


# ---------------------------------------------------------------------------
# 中文版文本编辑节点（单步、可串联）
# ---------------------------------------------------------------------------


class PromptTextEditorV21CN:
    """单步文本编辑节点（中文界面），可串联实现任意复杂编辑链。

    编辑模式：
      - 替换(replace)   : 把所有匹配的 *查找* 文本替换为 *替换为*
      - 前缀(prepend)   : 在每个 *查找* 匹配的前面插入 *替换为*
      - 后缀(append)    : 在每个 *查找* 匹配的后面插入 *替换为*
      - 删除(delete)    : 移除所有匹配的 *查找* 文本

    勾选 *正则表达式* 后，*查找* 会按正则规则匹配。
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "文本": ("STRING", {"forceInput": True}),
                "编辑模式": (
                    ["替换(replace)", "前缀(prepend)", "后缀(append)", "删除(delete)"],
                    {"default": "替换(replace)"},
                ),
                "查找": ("STRING", {"default": "", "multiline": True}),
                "替换为": ("STRING", {"default": "", "multiline": True}),
                "正则表达式": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("编辑后文本",)
    FUNCTION = "编辑"
    CATEGORY = "提示词"

    def 编辑(
        self,
        文本: str,
        编辑模式: str,
        查找: str,
        替换为: str,
        正则表达式: bool,
    ) -> Tuple[str]:
        mode = 编辑模式.split("(")[1].rstrip(")") if "(" in 编辑模式 else 编辑模式

        if not 查找:
            return (文本,)

        try:
            if 正则表达式:
                _pattern = re.compile(查找)
            else:
                _pattern = re.compile(re.escape(查找))
        except re.error as exc:
            print(f"[文本编辑:中文版V2.1] 正则错误：{exc}")
            return (文本,)

        if mode == "replace":
            result = _pattern.sub(lambda m: 替换为, 文本)
        elif mode == "prepend":
            result = _pattern.sub(lambda m: 替换为 + m.group(0), 文本)
        elif mode == "append":
            result = _pattern.sub(lambda m: m.group(0) + 替换为, 文本)
        elif mode == "delete":
            result = _pattern.sub("", 文本)
        else:
            result = 文本

        return (result,)


# ---------------------------------------------------------------------------
# 注册
# ---------------------------------------------------------------------------

NODE_CLASS_MAPPINGS = {
    "ComfyUI_Prompt_Library_V21_CN": PromptLibraryLoaderV21CN,
    "ComfyUI_Prompt_Preview_V21_CN": PromptPreviewV21CN,
    "ComfyUI_Prompt_Text_Editor_CN": PromptTextEditorV21CN,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ComfyUI_Prompt_Library_V21_CN": "提示词库加载器（中文版 V2.1）",
    "ComfyUI_Prompt_Preview_V21_CN": "提示词预览（中文版 V2.1）",
    "ComfyUI_Prompt_Text_Editor_CN": "文本编辑（中文版 V2.1）",
}
