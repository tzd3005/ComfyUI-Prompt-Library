"""ComfyUI 提示词库 — 中文版自定义节点。

界面与输出文案全部中文化；节点 className 以 _CN 结尾，与 V2 英文版共存不冲突。
自带前端文本预览（靠 web/ JS 渲染只读显示窗口）。
"""

from .nodes_cn import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# 声明前端扩展目录（ComfyUI 官方标准加载方式）
WEB_DIRECTORY = "./web"

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY",
]
