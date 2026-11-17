# Changelog

## 1.2 — 2026-11-18

- `report_lib.build()` 一次产出五个文件：桌面 html、手机 html、md、单文件 md（data URI）、飞书 md。
- 新增手机版渲染：单列自适应、顶部胶囊导航、结构图竖排、表格横滚、点图全屏、回到顶部；图片按 760px/q72 重压，体积约为桌面版一半。
- 新增单文件 Markdown：图片以 `<img src="data:image/jpeg;base64,...">` 内嵌，单个 .md 即可转发。
- 新增可选 `EXTRA_TABLES`：对比表、外部信息核对、风险清单等任意表格，HTML 与 MD 同步渲染。
- 新增可选 `HTML_NAME` / `MOBILE_NAME`：在 md 顶部写出两个 html 的文件名。
- 修复手机版卡片类名（`.card` → `.m-card`）、表格撑破视口（`table-layout:fixed` + `overflow-wrap:anywhere`）。
- 手机版页面索引改为卡片列表（原表格在 390px 下被压成每列 1 个字）。\n- 示例 `etalien-pc.json` 用真实报告回填 17 页的 desc/points，并补了 3 张 EXTRA_TABLES。

## 1.1 — 2026-11-18

- `report_lib.py`：一条命令出三份（`<SLUG>.html` / `<SLUG>.md` / `feishu_doc.md`），新增可选 `LANES`/`ROWS`/`TABS` 可视结构图（节点可点跳转）。
- 修复 `shots/shots/` 双前缀 bug：`feishu_doc.md` 现在是 `@./shots/xx.jpg`。
- 新增 `references/writing.md`：结论/页面描述/层级树写法，含反例→正例对照。
- 重写 `references/report.md`：JSON 字段全表（大写键、`img` 不带扩展名、`CLEAN/TECH/OBSERVE/METHOD`）。
- 新增 `examples/etalien-pc.json` + `README.md`：外星仔 PC 版 17 页真实数据。
- 新增 `scripts/verify_report.py`：图片缺失、索引/卡片数量不一致、编号重复、章节缺失、正文过短，一次查完。
- 新增 `scripts/adb.ps1`：Android 的 devices/packages/start/shot/dump/tap/swipe/text/back。
- `SKILL.md` 增加“包内地图”与时间预算；校验步骤改为跑 `verify_report.py`。

## 1.0 — 2026-11-17

- 首个版本：流程、Windows/Android 操作、静态取证、外部调研、报告格式、硬规则。
- 脚本：`win_cap.ps1`、`win_ctl.ps1`、`win_admin.ps1`、`cap.ps1`、`make_shots.py`。
- 模板：`report.md`、`report.json`。
- 补充：飞书发布（lark-cli）与手机截图坐标换算等硬规则。
