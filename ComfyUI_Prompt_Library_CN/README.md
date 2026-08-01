# ComfyUI Prompt Library CN（中文版）

ComfyUI 提示词库管理节点（中文界面）。从 `prompt_library/` 文件夹的 `.txt` 中按模式抽取提示词，并输出行号摘要 + 自带文本预览。

## 节点
- `ComfyUI_Prompt_Library_CN` — 提示词库加载器（输入 提示词文件/抽取模式/手动指定行/自动重载文件；输出 提示词 + 摘要）
- `ComfyUI_Prompt_Preview_CN` — 提示词预览（自带显示窗口）

## 安装
1. 将本文件夹复制到 `ComfyUI/custom_nodes/`（目录名保持 `ComfyUI_Prompt_Library_CN`）
2. **重启 ComfyUI**（前端 JS 加载必需，勿只刷新浏览器）

## 使用
1. 在 ComfyUI 根目录建 `prompt_library/`，放 `.txt`（每行一条，`#//;` 开头为注释）
2. 加载器选文件 + 模式，执行后 `摘要` 输出 `[文件 | 第X/Y行]`
3. 拖 `提示词`/`摘要` 到 `提示词预览` 的 `文本` 口预览

## 示例工作流
`ComfyUI_Prompt_Library_CN.json` 为可直接导入的 Z-image 文生图工作流（依赖 Z-image 相关模型）。
