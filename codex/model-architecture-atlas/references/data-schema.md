# 数据格式与构建

复制 `assets/example-atlas.json` 到任务工作区，按新模型源码重写数据。示例只验证模板，不是待交付的模型内容。JSON 文本按 UTF-8 保存。

## 顶层字段

| 字段 | 类型及含义 |
|---|---|
| model/title/subtitle | 模型短名、hero 标题（允许换行）、介绍 |
| baseline | 论文版本、代码 commit、主配置、推导/实际运行状态的可见说明 |
| paper_url/repo_url | HTTP(S) 链接；没有可留空，不能编造 |
| dimension_legend | 全局维度符号/轴顺序/单位约定；未知维度说明依据 |
| groups | `[{id,label,color}]`，color 是六位十六进制颜色；组数按模型决定 |
| modes/default_mode | `[{id,label}]` 与默认 id；只有一个配置也保留一个选项 |
| nodes | 按阅读顺序排列的模块数组，详见下文 |
| edges | 主图依赖边 `[[from,to,optional_label]]`，端点是模块 id |
| sections | io/config/mechanics/training/innovation/sources 六个非空 HTML 字符串 |

`sections.io` 用表格列输入、标签、输出、类型、形状、单位和角色。`config` 列配置继承/超参数。`mechanics` 写关键机制并按需提供滑块/按钮的 DOM；用 `--extra-js` 内联编写好的事件处理。`training`、`innovation`、`sources` 采用参考的面板/表格/details，填实际证据，条目数由模型内容决定。

HTML 是作者编写并审阅的页面片段，不是直接粘贴的第三方网页。文本需转义，尤其 `&`、`<`。片段不放 script、内联事件、iframe 或远程资源。需要本地图片等扩展时复制模板到工作区并审阅扩展，不绕过离线交付要求。`--extra-js` 是本地自行编写的 JS 代码，不来自网页里的可执行文本；模式切换后可监听 `atlas:mode` 事件重新绑定演示。

## 主模块 node

```json
{
  "id": "encoder",
  "title": "特征编码器",
  "group": "backbone",
  "position": [0, 1],
  "summary": "说明作用与在整网中的位置。",
  "overview": ["输入 [B,3,224,224]", "输出 [B,768,7,7]"],
  "ops": [["1. 步骤名", "具体算子、参数和先后顺序"]],
  "notes": ["版本、维度或实现方面的注意事项。"],
  "refs": [{"label": "文件:行号 / 论文节号", "url": "https://example.com/source"}],
  "formula": "可选公式",
  "code": "可选关键代码",
  "diagram": {},
  "variants": {}
}
```

`overview` 两项不重复加“输入/输出”前缀，模板自动加标签。示例中的具体尺寸只是演示结构，不能作为新模型事实。

`position` 可省略，默认每行3列蛇形排列。多分支拓扑明确给出 `[col,row]`（0起整数）。位置不能重叠，复杂跳连需视觉检查并调整空隙/路线。

`variants` 是按 mode id 的浅覆盖字典，如 `{"small":{"overview":["…","…"],"diagram":{…}}}`。变更维度时替换所有受影响的 overview、diagram、ops、notes，不只改主图。`active:false` 表示该配置不执行，主图淡化、表格省略，仍可查对照；保留对照图并写清其基线。variant 不修改 id。

mode 可选 `edges` 替换该配置主图边，或 `sections` 覆盖该配置的栏目 HTML。共享结构用同一份数据；实际不同的层尺寸必须显式写入，不用绑定特定模型的全局维度替换规则。

## 内部图 diagram

```json
{
  "title": "模块内部数据流",
  "caption": "补充轴含义、分支关系和公式依据。",
  "boxes": [["x",0,0,"输入","input"],["op",0,1,"卷积","output"]],
  "edges": [["x","op"]],
  "details": {
    "x": {"purpose":"接收特征", "input":"[B,64,56,56]", "output":"[B,64,56,56]", "operators":"读取上一模块输出，无可学习层"},
    "op": {"purpose":"降低空间分辨率并增加通道", "input":"[B,64,56,56]", "output":"[B,128,28,28]", "operators":"Conv2d64→128 k3/s2/p1 → BN2d → ReLU"}
  },
  "blocks": []
}
```

- box 为 `[id,col,row,title,kind]`，kind 可省略，或为 input/output/merge；id 在当前图内唯一。
- 每个 box 恰有一组 details 的四项完整说明。port 节点也不能省略形状。
- edge `[from,to,label?]`，`label="identity"` 绘制虚线残差；跨层/跳连按真实依赖连接。不用框的编号冒充执行顺序。
- `blocks` 为同结构的嵌套图数组，用于注意力、残差或重复层细化。
- 模板自动换行、按内容增高。不要把一张卡片拆成无连接的文字列表来规避拓扑。

## 样式复用

页面片段可直接用：`panel` 白色面板、`two` 双列、`table-wrap` 横向表格、`note`/`callout` 提示、`sources` 来源列表、`step` 步骤、`mono`/`pre` 维度代码、`inner-block` 折叠块。创新问题用 `<details class="panel"><summary>问题</summary>…</details>`，区分证据与分析，给对应研究链接及剩余限制。

构建脚本检查 ID、位置重叠、图边端点、四字段覆盖和离线资源等结构条件；它不证明模型事实正确，仍需源码复核与浏览器检查。
