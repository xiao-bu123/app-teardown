# 报告格式：JSON → MD / HTML / 飞书（一条命令）

## 1. 数据文件（唯一输入）

把整份报告写成 **一个 JSON**，图片放 `shots/`，然后：

```powershell
python scripts\build_report.py my_report.json --root .
# 产出五个文件：
#   <SLUG>.html          桌面版，单文件，截图 base64 内嵌，含可视结构图
#   <SLUG>_mobile.html   手机版，单列自适应，图片 760px 重压，体积约一半
#   <SLUG>.md            Markdown，图片引用 shots/xx.jpg
#   <SLUG>_single.md     单文件 Markdown，图片内嵌 data URI（可单独发人）
#   feishu_doc.md        飞书版，图片路径 @./shots/xx.jpg
```

- 手机版：顶部胶囊导航、结构图竖排、表格横向滚动、点图全屏；可直接传手机用浏览器打开。
- 单文件 Markdown：`<img src="data:image/jpeg;base64,...">`。Typora / VS Code 可显示，GitHub 不渲染 data URI，介意就发 `md + shots/` 或直接发桌面版 html。
- 想改手机版图片质量/宽度：`build_mobile()` 里的 `maxw=760, quality=72`。

示例数据：`examples/etalien-pc.json`（17 页真实项目）。

## 2. 字段表

顶层（大小写敏感，全部是属性名）：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `SLUG` | string | ✅ | 输出文件主名，如 `etalien_pc` |
| `TITLE` / `SUB` | string | ✅ | 标题 / 副标题 |
| `META` | `[[键, 值]]` | ✅ | 基本盘表格；值里可带 `<code>` 等 HTML |
| `CONCLUSIONS` | `[[标题, 正文]]` | ✅ | 4–5 条 |
| `TREE` | string | ✅ | 文本层级树，原样放进 `<pre>` |
| `SECTIONS` | `[{id, num, title, intro, pages}]` | ✅ | 逐页拆解分组；`num` 是 "1"/"2" |
| `CLEAN` | `[[...]]` | ✅ | 功能清单表，第一行是表头 |
| `TECH` | `[[维度, 结论]]` | ✅ | 技术观察 |
| `OBSERVE` | `[[标题, 段落或数组]]` | ✅ | 产品判断，固定三块：主要功能 / 商业变现 / 活动运营；第二项可写数组，渲染成多条要点 |
| `METHOD` | `[string]` | ✅ | 方法与边界（列表项） |
| `LANES` | `[{title, nodes}]` | 可选 | 结构图泳道；有它才显示"页面结构图" |
| `ROWS` | `[{label, nodes}]` | 可选 | 弹窗层 / 隐藏层横排 |
| `TABS` | `[string]` | 可选 | 结构图顶部假 Tab 胶囊 |
| `MAP_INTRO` | string | 可选 | 结构图说明句 |
| `HERO_STATS` | `[[值, 说明]]` | 可选 | Hero 四个数字；缺省用页面数/Tab 数 |
| `BRAND` / `BRAND_SUB` | string | 可选 | 侧栏品牌名与小字 |
| `METRICS` | `[[指标, 数值, 时间, 来源, 性质]]` | 可选 | 第三方数据表（七麦/点点）；性质写 渠道公开 / 第三方估算 / 付费墙未获取 |
| `METRICS_NOTE` | string | 可选 | 第三方数据的口径说明 |
| `EXTRA_TABLES` | `[{id, title, head, rows}]` | 可选 | 额外表格（对比表 / 外部信息核对 / 风险清单），HTML 与 MD 同步输出 |
| `HTML_NAME` / `MOBILE_NAME` | string | 可选 | 在 md 顶部写出两个 html 的文件名，方便同目录互跳 |
| `IMG_DIR` | string | 可选 | 默认 `shots` |
| `NOTE` / `FOOTER` | string | 可选 | 方法区提示 / 页脚 |

`pages[]` 每项：

| 字段 | 说明 |
|---|---|
| `code` | `L0-01` 形式，唯一 |
| `name` / `path` / `kind` | 页面名 / 路径 / 类型标签（如 `[功能] 加速详情`） |
| `img` | **不带扩展名**，如 `01_steam_home`（渲染时补 `.jpg`） |
| `desc` | v1 的 1–2 句页面说明（v2 用 `role` 替代） |
| `role` | **v2**：一句定位，禁止方位词（顶部/左侧/右栏） |
| `blocks` | **v2**：区块数组，见下 |
| `shell` | **v2**：`true` 表示复用全局壳层 |
| `points` | 判断（为什么这么设计、风险），不再重复结构 |
| `unverified` | **v2**：没查清的点，渲染成「未查」 |
| `next` / `limit` | 跳转 / 限制（可选） |

`blocks` 每条：`[位置, 序, 区块名, 类型, 内容组成, 交互去向, 置信度]`

| 位 | 取值 |
|---|---|
| 位置 | `top / left / center / right / bottom / overlay` |
| 类型 | `nav / hero / list / detail / pay / ops / tool / form / status` |
| 置信度 | `seen / absent / inferred / unknown` |

顶层还有两个 **v2** 字段：`SHELL`（跨页复用的区块数组，同 blocks 格式）与 `SHELL_SCOPE`（说明哪些页复用，如「游戏详情页 L0-01 / L0-02」）。

`nodes` 每项：`[标签, 副标, kind, 跳转code]`，`kind ∈ func|content|pay|sys`，对应紫/绿/橙/蓝。

## 3. 结构图长什么样

- 五条（或 N 条）泳道横向并列，每条泳道是一个一级 Tab。
- 每条泳道里的节点用虚线串起来，节点是 `<a href="#页面code">`，点了直接跳到下方卡片。
- 泳道下面是 `ROWS`：弹窗层、隐藏窗口/内核。
- 右下角有颜色图例。

没有 `LANES` 时，HTML 只剩"文本树 + 卡片"，也可以交，但少了最值钱的那张图。

## 4. 写完之后

```powershell
python scripts\verify_report.py <SLUG>.md
```

检查：图片是否都存在、索引条数 = 卡片数、编号是否重复、章节是否齐全、正文是否过短。
`PASS` 才交付。

## 5. 飞书发布（可选）

`feishu_doc.md` 直接灌进飞书文档，命令与三个常见报错见 `SKILL.md` 的"发布到飞书"一节。

## 6. 截图规范

- 编号 = 页面索引顺序：`01_home`、`02_lib`……
- 宽度 1000px、JPEG q84（约 80–110 KB/张），用 `scripts/make_shots.py`。
- 暗色界面转 jpg 会偏灰，必要时 `ImageEnhance.Brightness(1.05)`。
- 原始 png 留在上一层目录（`p01_home.png`），便于重裁。

## 7. 页面编号

`L0-01`、`L1-09`、`L2-11`：L0 = 一级 Tab/首页，L1 = 二级页/弹窗，L2 = 三级页/支付/H5，L3 = 更深。
编号按叙述顺序，不按点击顺序。
