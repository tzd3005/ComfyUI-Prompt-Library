# ComfyUI Prompt Library V2.1（中文版）

ComfyUI 提示词库管理节点（中文界面）。在中文版 V2 功能（Loader + Preview）基础上，**新增单步文本编辑节点**。从 `prompt_library/` 文件夹的 `.txt` 中按模式抽取提示词，输出行号摘要 + 自带文本预览，并可按需对提示词做替换 / 前缀插入 / 后缀插入 / 删除编辑。

## 节点
- `ComfyUI_Prompt_Library_V21_CN` — 提示词库加载器（输入 提示词文件/抽取模式/手动指定行/自动重载文件；输出 提示词 + 摘要）
- `ComfyUI_Prompt_Preview_V21_CN` — 提示词预览（自带显示窗口）
- `ComfyUI_Prompt_Text_Editor_CN` — 文本编辑（单步、可串联）

## 文本编辑节点
单步执行一种编辑操作，支持串联（上一个节点的 `编辑后文本` 接到下一个节点的 `文本`），即可构建任意复杂的编辑链。

参数：
| 参数 | 说明 |
|------|------|
| 文本 | 待编辑文本（forceInput，从上方节点接入） |
| 编辑模式 | `替换(replace)` / `前缀(prepend)` / `后缀(append)` / `删除(delete)` |
| 查找 | 要定位的字符。`替换`/`删除` 的目标，`前缀`/`后缀` 的插入锚点 |
| 替换为 | 替换成的内容（`替换`），或要插入的内容（`前缀`/`后缀`） |
| 正则表达式 | 勾选后 `查找` 按正则表达式匹配 |

编辑逻辑：
- `替换`：把所有匹配的 `查找` 替换为 `替换为`
- `前缀`：在每个 `查找` 匹配的前面插入 `替换为`
- `后缀`：在每个 `查找` 匹配的后面插入 `替换为`
- `删除`：移除所有匹配的 `查找`

示例：把 `ComfyUI` 替换成 `ComfyUI!`，或将 `masterpiece` 前加前缀 `best quality, `。

## 安装
1. 将本文件夹复制到 `ComfyUI/custom_nodes/`（目录名保持 `ComfyUI_Prompt_Library_V21_CN`）
2. **重启 ComfyUI**（前端 JS 加载必需，勿只刷新浏览器）

## 使用
1. 在本插件目录内建 `prompt_library/`，放 `.txt`（每行一条，`#//;` 开头为注释）。目录不存在时插件会自动创建，路径为：

   ```
   ComfyUI/custom_nodes/ComfyUI_Prompt_Library_V21_CN/prompt_library/
       ├── girl.txt
       ├── landscape.txt
       └── anime/
           ├── cute.txt
           └── realistic.txt
   ```

   > ⚠️ 与 V2 不同：V2.1 的 `prompt_library` **放在插件自身目录内**，而不是 ComfyUI 根目录。

2. 加载器选文件 + 模式，执行后 `摘要` 输出 `[文件 | 第X/Y行]`
3. 拖 `提示词`/`摘要` 到 `提示词预览` 的 `文本` 口预览
4. 可选：在中间串接 `文本编辑` 对提示词做编辑

## 与其他版本
V2.1 与 V2 / 英文版节点 className 不冲突，可同时安装。
