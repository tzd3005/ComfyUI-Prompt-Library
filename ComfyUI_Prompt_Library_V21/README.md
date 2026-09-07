# ComfyUI Prompt Library V2.1（英文版）

ComfyUI 提示词库管理节点（英文界面）。在 V2 功能（Loader + Preview）基础上，**新增单步文本编辑节点**。从 `prompt_library/` 文件夹的 `.txt` 中按模式抽取提示词，输出行号摘要 + 自带文本预览，并可按需对提示词做替换 / 前缀插入 / 后缀插入 / 删除编辑。

## 节点
- `ComfyUI_Prompt_Library_V21` — 提示词加载器（输入 prompt_file / mode / manual_line / auto_reload；输出 prompt + summary）
- `ComfyUI_Prompt_Preview_V21` — 文本预览（自带显示窗口）
- `ComfyUI_Prompt_Text_Editor` — 文本编辑（单步、可串联）

## 文本编辑节点
单步执行一种编辑操作，支持串联（上一个节点的 `edited` 接到下一个节点的 `text`），即可构建任意复杂的编辑链。

参数：
| 参数 | 说明 |
|------|------|
| text | 待编辑文本（forceInput，从上方节点接入） |
| mode | 编辑类型：`replace` / `prepend` / `append` / `delete` |
| find | 要定位的字符。`replace`/`delete` 的目标，`prepend`/`append` 的插入锚点 |
| replacement | 替换成的内容（`replace`），或要插入的内容（`prepend`/`append`） |
| regex | 勾选后 `find` 按正则表达式匹配 |

编辑逻辑：
- `replace`：把所有匹配的 `find` 替换为 `replacement`
- `prepend`：在每个 `find` 匹配的前面插入 `replacement`
- `append`：在每个 `find` 匹配的后面插入 `replacement`
- `delete`：移除所有匹配的 `find`

示例：把 `ComfyUI` 替换成 `ComfyUI!`，或将 `masterpiece` 前加前缀 `best quality, `。

## 安装
1. 将本文件夹复制到 `ComfyUI/custom_nodes/`（目录名保持 `ComfyUI_Prompt_Library_V21`）
2. **重启 ComfyUI**（前端 JS 加载必需，勿只刷新浏览器）

## 使用
1. 在本插件目录内建 `prompt_library/`，放 `.txt`（每行一条，`#//;` 开头为注释）。目录不存在时插件会自动创建，路径为：

   ```
   ComfyUI/custom_nodes/ComfyUI_Prompt_Library_V21/prompt_library/
       ├── girl.txt
       ├── landscape.txt
       └── anime/
           ├── cute.txt
           └── realistic.txt
   ```

   > ⚠️ 与 V2 不同：V2.1 的 `prompt_library` **放在插件自身目录内**，而不是 ComfyUI 根目录。

2. 加载器选文件 + 模式，执行后 `summary` 输出 `[file | X/Y]`
3. 拖 `prompt`/`summary` 到 `ComfyUI_Prompt_Preview_V21` 的 `text` 口预览
4. 可选：在中间串接 `ComfyUI_Prompt_Text_Editor` 对提示词做编辑

## 与其他版本
V2.1 与 V2 / CN 版本节点 className 不冲突，可同时安装。

## 中文版
如需中文界面，使用同仓库的 `ComfyUI_Prompt_Library_V21_CN`。
