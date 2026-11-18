# Changelog

## 1.5 — 2026-11-18

- 产品判断改为三个固定小节（1. 主要功能 / 2. 商业变现 / 3. 活动运营），全宽堆叠，每节可写 3–5 条要点（`OBSERVE` 第二项支持数组）。
- 手机版第三方数据改为「指标 + 数值 / 时间·来源·性质」两行卡片，390px 下不再挤成五列。
- 桌面产品判断由两列卡片改为全宽区块，长列表可读性更好。

## 1.4 — 2026-11-18

- 新增第三方数据 `METRICS` / `METRICS_NOTE`：七麦、点点的 DAU/MAU、下载量、榜单排名，五列「指标 / 数值 / 时间 / 来源 / 性质」，性质区分 渠道公开 / 第三方估算 / 付费墙未获取。
- 桌面版在基本盘后新增「第三方数据」区块；手机版同步；Markdown 作为「基本盘」的子表输出。
- `references/external.md` 新增 3.5 节：第三方数据来源、口径与三条禁则（拿不到就写未获取、估算不进结论、不为取数注册付费）。
- 产品判断收窄为固定三块：**主要功能 / 商业变现 / 活动运营**，不再写「竞品是谁」这类推测。
- `SKILL.md` 的流程第 4 步与质量基线同步上述两条规则。

## 1.3 — 2026-11-18

- 新增 v2「页面内区块拆解」：每页 `role` + `blocks`（位置 / 序 / 区块 / 类型 / 内容 / 交互 / 置信度），支持 `seen / absent / inferred / unknown` 四态。
- 新增全局壳层 `SHELL` + `SHELL_SCOPE`：顶栏、右栏、底部卡只写一次，页面用 `shell: true` 引用。
- 桌面卡片改为整行宽卡：截图 + 七列区块表 + 判断；手机版区块改为卡片列表。
- `verify_report.py` 新增区块检查：`定位` / `区块` 表数量、区块行数、absent/unknown 统计。
- `examples/etalien-pc.json` 更新为 v2（17 页 / 71 区块 / 8 处「确认没有」/ 4 处「未查」）。
- 修复 `_index_rows` 与 Markdown 索引对 `desc` 的硬依赖，兼容只写 `role` 的页面。

## 1.2 — 2026-11-18

- `report_lib.build()` 一次产出五个文件：桌面 html、手机 html、md、单文件 md（data URI）、飞书 md。
- 新增手机版渲染：单列自适应、顶部胶囊导航、结构图竖排、表格横滚、点图全屏、回到顶部；图片按 760px / q72 重压，体积约为桌面版一半。
- 新增单文件 Markdown：图片以 `<img src="data:image/jpeg;base64,...">` 内嵌，单个 .md 即可转发。
- 新增可选 `EXTRA_TABLES`：对比表、外部信息核对、风险清单等任意表格，HTML 与 MD 同步渲染。
- 新增可选 `HTML_NAME` / `MOBILE_NAME`：在 md 顶部写出两个 html 的文件名。
- 修复手机版卡片类名（`.card` → `.m-card`）、表格撑破视口（`table-layout:fixed` + `overflow-wrap:anywhere`）。
- 手机版页面索引改为卡片列表（原表格在 390px 下被压成每列 1 个字）。
- 示例 `etalien-pc.json` 用真实报告回填 17 页的 desc / points，并补了 3 张 `EXTRA_TABLES`。

## 1.1 — 2026-11-18

- `report_lib.py`：一条命令出三份（`<SLUG>.html` / `<SLUG>.md` / `feishu_doc.md`），新增可选 `LANES` / `ROWS` / `TABS` 可视结构图（节点可点跳转）。
- 修复 `shots/shots/` 双前缀 bug：`feishu_doc.md` 现在是 `@./shots/xx.jpg`。
- 新增 `references/writing.md`：结论 / 页面描述 / 层级树写法，含反例→正例对照。
- 重写 `references/report.md`：JSON 字段全表（大写键、`img` 不带扩展名、`CLEAN/TECH/OBSERVE/METHOD`）。
- 新增 `examples/etalien-pc.json` + `README.md`：外星仔 PC 版 17 页真实数据。
- 新增 `scripts/verify_report.py`：图片缺失、索引/卡片数量不一致、编号重复、章节缺失、正文过短，一次查完。
- 新增 `scripts/adb.ps1`：Android 的 devices / packages / start / shot / dump / tap / swipe / text / back。
- `SKILL.md` 增加「包内地图」与时间预算；校验步骤改为跑 `verify_report.py`。

## 1.0 — 2026-11-17

- 首个版本：流程、Windows/Android 操作、静态取证、外部调研、报告格式、硬规则。
- 脚本：`win_cap.ps1`、`win_ctl.ps1`、`win_admin.ps1`、`cap.ps1`、`make_shots.py`。
- 模板：`report.md`、`report.json`。
- 补充：飞书发布（lark-cli）与手机截图坐标换算等硬规则。
