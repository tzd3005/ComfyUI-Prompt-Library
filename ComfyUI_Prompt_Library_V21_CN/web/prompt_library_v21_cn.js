// ComfyUI Prompt Library V2.1（中文版）— 前端文本预览扩展
// 原理与 AlekPet 的 PreviewTextNode 一致：
//   - 后端返回 {"ui": {"string": [text]}}
//   - 前端在节点创建时用 ComfyWidgets.STRING 挂一个只读文本框 widget
//   - onExecuted 钩子把后端返回的 ui.string 写入该文本框
//
// 必须配合后端节点名 "ComfyUI_Prompt_Preview_V21_CN" 使用。

import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

app.registerExtension({
  name: "ComfyUI_Prompt_Library_V21_CN.PromptPreview",

  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeData.name !== "ComfyUI_Prompt_Preview_V21_CN") {
      return;
    }

    // --- 节点创建时：挂一个只读文本框 widget ---
    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const ret = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

      // 用实例号保证多节点共存时 widget 名唯一
      const count = app.graph._nodes.filter(
        (n) => n.type === "ComfyUI_Prompt_Preview_V21_CN"
      ).length;
      const widgetName = `preview_text_${count}`;

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
        wi.widget.inputEl.readOnly = true; // 只读，防止手动乱改
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

      // 找到我们创建的只读文本框
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
