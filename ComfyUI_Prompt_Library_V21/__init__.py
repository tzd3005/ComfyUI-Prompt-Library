"""ComfyUI Prompt Library V2.1 — standalone custom node for large prompt libraries.

V2.1 相对 V2 的新增:
  1. 新增单步文本编辑节点（替换/前缀/后缀/删除，支持正则，可串联）。
  2. 保留 V2 的全部功能（Loader + Preview）。

节点 className 均带 V21 后缀（除独立的文本编辑节点外），与 V2/CN 版本共存不冲突。
"""

from .nodes_v21 import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# 声明前端扩展目录（ComfyUI 官方标准加载方式）
WEB_DIRECTORY = "./web"

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
]
