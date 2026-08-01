"""ComfyUI Prompt Library V2 — standalone custom node for large prompt libraries.

V2 改进（相对 v1）:
  1. 输出 prompt + summary（summary 含 [文件 | 行号/总数] 诊断文本）。
  2. 修复 manual_line 割裂 bug：手动指定后同步更新持久 state。
  3. 自带前端文本预览节点 Prompt Preview（与 AlekPet 同款机制，靠 web/ JS 渲染）。
"""

from .nodes_v2 import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# 声明前端扩展目录（ComfyUI 官方标准加载方式）
WEB_DIRECTORY = "./web"

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
]
