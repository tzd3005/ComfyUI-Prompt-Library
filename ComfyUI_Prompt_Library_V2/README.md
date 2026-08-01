# ComfyUI Prompt Library V2（英文版）

ComfyUI 提示词库管理节点（英文界面）。从 `prompt_library/` 文件夹的 `.txt` 中按模式抽取提示词，并输出行号摘要 + 自带文本预览。

## 节点
- `ComfyUI_Prompt_Library_V2` — 提示词加载器（输入 prompt_file / mode / manual_line / auto_reload；输出 prompt + summary）
- `ComfyUI_Prompt_Preview` — 文本预览（自带显示窗口）

## 安装
1. 将本文件夹复制到 `ComfyUI/custom_nodes/`（目录名保持 `ComfyUI_Prompt_Library_V2`）
2. **重启 ComfyUI**（前端 JS 加载必需，勿只刷新浏览器）

## 使用
1. 在 ComfyUI 根目录建 `prompt_library/`，放 `.txt`（每行一条，`#//;` 开头为注释）
2. 加载器选文件 + 模式，执行后 `summary` 输出 `[file | X/Y]`
3. 拖 `prompt`/`summary` 到 `ComfyUI_Prompt_Preview` 的 `text` 口预览

## 中文版
如需中文界面，使用同仓库的 `ComfyUI_Prompt_Library_CN`。
