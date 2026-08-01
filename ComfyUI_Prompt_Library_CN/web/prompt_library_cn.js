// ComfyUI 提示词库 — 中文版 前端预览扩展
// 与 V2 版同款机制：onExecuted 把后端返回的 ui.string 写入只读文本框。
// 必须配合后端节点 className "ComfyUI_Prompt_Preview_CN" 使用。

import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

app.registerExtension({
  name: "ComfyUI_Prompt_Library_CN.PromptPreview",

  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeData.name !== "ComfyUI_Prompt_Preview_CN") {
      return;
    }

    // --- 节点创建时：挂只读文本框 ---
    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const ret = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

      const count = app.graph._nodes.filter(
        (n) => n.type === "ComfyUI_Prompt_Preview_CN"
      ).length;
      const widgetName = `cn_preview_text_${count}`;

      const wi = ComfyWidgets.STRING(
        this,
        widgetName,
        [
          "STRING",
          {
            default: "",
            placeholder: "提示词输出预览...",
            multiline: true,
          },
        ],
        app
      );
      if (wi?.widget) {
        wi.widget.inputEl.readOnly = true;
      }

      this.setSize(this.computeSize(this.size));
      app.graph.setDirtyCanvas(true, false);

      return ret;
    };

    // --- 执行结果写入文本框 ---
    const onExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function (executed) {
      onExecuted?.apply(this, arguments);

      const texts = executed?.string;
      if (!texts || texts.length === 0) {
        return;
      }

      const widget = this.widgets.find((w) => w.type === "customtext");
      if (!widget) {
        return;
      }

      let value = Array.isArray(texts)
        ? texts
            .map((v) => (typeof v === "object" ? JSON.stringify(v) : String(v)))
            .filter((s) => s.trim() !== "")
            .join("\n")
        : String(texts);

      widget.value = value;
      app.graph.setDirtyCanvas(true);
    };
  },
});
