---
name: app-teardown
description: Research an installed app or Windows desktop client end-to-end — launch it, capture every reachable page as screenshots, then deliver a page hierarchy tree, per-page breakdown, feature list, tech forensics and a self-contained HTML report. Use when asked to 调研 / 拆解 / 扒 / 做页面树 for a mobile app, a PC client, or a web app.
whenToUse: The user asks to 调研某个 App / 客户端 / 软件, wants a 页面层级树 / 功能清单 / 页面结构图 / 竞品拆解, or references a previous 调研 report and asks for the same treatment on another product.
---

# App / 客户端逐页调研（页面树 + 功能清单）

一套可复用的"装到机器上、逐页点开、拍下来、写成文档"的流程。适用于 Android App、Windows 桌面客户端、以及内嵌 H5 的产品。

## 包内地图（SKILL.md 只是目录，干活的是下面这些）

| 文件 | 什么时候看 |
|---|---|
| `references/windows.md` | 目标是 Windows 客户端（截图 / 点击 / 提权） |
| `references/android.md` | 目标是 Android App（adb / uiautomator） |
| `references/forensics.md` | 做安装目录与系统取证 |
| `references/external.md` | 查官网 / 定价 / 主体 / 口碑 / 竞品 |
| `references/writing.md` | 写结论和页面描述前（反例→正例） |
| `references/report.md` | JSON 字段全表、三种产出、截图规范 |
| `references/pitfalls.md` | 卡住时先翻（15 条真实踩坑） |
| `examples/etalien-pc.json` | 要抄数据结构时（真实项目 17 页） |
| `scripts/win_cap.ps1` | 按窗口类名截图；`-list` 枚举所有窗口 |
| `scripts/win_ctl.ps1` | 序列化点击：`-seq "click:165,41\|cap:..."` |
| `scripts/win_admin.ps1` | 目标以管理员运行时，用同权限执行 |
| `scripts/adb.ps1` | Android 的 shot / dump / tap / swipe / text |
| `scripts/make_shots.py` | png → jpg（1000px，q84） |
| `scripts/build_report.py` | JSON → HTML + MD + 飞书版，一条命令 |
| `scripts/report_lib.py` | 渲染器（build_report 依赖，别单独改接口） |
| `scripts/verify_report.py` | 交付前自检（图片 / 条数 / 编号 / 章节） |
| `templates/report.md` / `report.json` | 报告骨架 / 数据模板 |

**时间预算**：摸底 5 分钟 + 静态取证 15 分钟 + 逐页下钻 30–50 分钟 + 外部调研 20 分钟 + 写文档 40 分钟。超过 3 小时说明范围没收敛。

## 产出物（一次交付四件）

| 文件 | 说明 |
|---|---|
| `<产品>_页面层级树与功能清单.md` | 主报告：基本盘、结论、层级树、页面索引、逐页拆解、功能清单、技术观察、产品判断、方法边界；图片引用 `shots/` |
| `<产品>_单文件版.md` | 同上，但图片内嵌为 data URI（`<img src="data:image/jpeg;base64,...">`），单个 .md 就能发给别人；部分渲染器（GitHub）不显示 data URI，本地 Typora/VS Code 正常 |
| `<产品>_页面树.html` | **桌面版**单文件：侧栏导航 + 可视结构图（截图节点）+ 卡片 + 表格，图片 base64 内嵌，双击即开 |
| `<产品>_页面树_手机版.html` | **手机版**单文件：单列自适应、顶部胶囊导航、结构图竖排、表格横滑、点图全屏；图片按 760px 重压，体积约为桌面版一半 |
| `feishu_doc.md` | 图片路径 `@./shots/`，直接用 lark-cli 写入飞书 |

页面数量目标：**≥ 15 个页面/状态**。少于 10 个通常意味着下钻不够或漏了弹窗层。

三条命令出全部产物（`scripts/` 与 `templates/` 可直接复制到调研目录）：

```powershell
python scripts\make_shots.py <png目录> .\shots            # png → shots/*.jpg（1000px）
python scripts\build_report.py my_report.json --root .    # → 桌面 html / 手机 html / md / 单文件 md / 飞书 md
python scripts\verify_report.py my_report.md              # 交付前自检
# 报告内容写在 JSON 里（结构见 templates/report.json），不要把文案焊进脚本
```

## 流程

### 0. 先摸清对象（5 分钟，别急着点）

- 找安装位置：卸载注册表 → `DisplayName / DisplayVersion / Publisher / InstallLocation`；开始菜单与桌面快捷方式。
- 确认是哪个端：Windows 客户端 / Android（`adb shell pm list packages | findstr <关键字>`）/ 纯 Web。
- 记下版本号、签名主体、安装时间——这些直接进报告"基本盘"。
- 看有没有已登录账号：客户端缓存、`shared_preferences`、hive、Cookies。**账号状态决定你能不能看到内页。**

### 1. 静态取证（可与运行并行）

读 `references/forensics.md`。最少拿到：安装体积与文件数、exe 签名、内核驱动/服务、网络端点、H5 域名、设备指纹。

### 2. 跑起来并截图

- **Android**：读 `references/android.md`（adb + uiautomator dump + screencap + 坐标点击）；`scripts/cap.ps1` 是现成的「截图 + 控件树文本」脚本，复制到调研目录直接用。
- **Windows**：读 `references/windows.md`（窗口捕获 + 相对移动闭环点击 + 提权）；`scripts/win_ctl.ps1` 负责列窗/截图/点击，`scripts/win_admin.ps1` 负责以管理员身份跑同一个脚本。
- 关键：**先确认输入能进去**。点一个 tab，截图对比；如果画面纹丝不动，不要继续点，去看"输入为什么被丢"（见 pitfalls 第 1 条）。

### 3. 逐页下钻（L0 → L3）

1. 一级 Tab 全部点一遍，每个 Tab 截 1 张（首屏）。
2. 每个 Tab 里点 1–2 个代表性子项（弹窗、详情、二级页）。
3. 弹窗层单独算页面：设置、账号、兑换、支付、权限请求。
4. 列表页滚动一屏，确认"还有没有更多"。
5. 碰到"点了没反应"，先在报告里记为缺陷，不要反复点（可能是前置条件不满足或二次确认缺失，见 pitfalls）。

分页命名：`01_xxx.jpg` 顺序编号，编号顺序 = 报告里页面索引的顺序。

**每页顺手拆区块（v2 核心）**：截完一张图，立刻写 3–6 条 `blocks`，字段是
`[位置, 序, 区块名, 类型, 内容组成, 交互去向, 置信度]`：

- 位置：`top / left / center / right / bottom / overlay`，按阅读顺序排。
- 类型：`nav / hero / list / detail / pay / ops / tool / form / status`（固定枚举，别自创）。
- 置信度：`seen` 截图可见；`absent` 专门查过确认没有；`inferred` 推断；`unknown` 未查清。
- 跨页完全相同的区块（顶栏、右栏、底部卡）提到 `SHELL` 只写一次，页面用 `shell: true` 引用。
- `role` 只写一句定位，**出现「顶部/左侧/右栏」这类方位词就说明该写进 blocks**。

### 4. 外部信息（15–20 分钟）

读 `references/external.md`。至少覆盖：官网最新版本、定价、主体/备案、口碑与投诉、合规背景、竞品价格，以及**第三方数据**（七麦 / 点点的 DAU、MAU、下载量、榜单排名）。第三方数据要标来源、日期与「渠道公开 / 第三方估算 / 付费墙未获取」，拿不到就写「未获取」，不引用二手转述。
**一手截图永远优先于二手说法**——本次就有外部调研说"PC 端没有时长包"，被客户端截图直接推翻。

### 5. 写文档

- 报告骨架：`templates/report.md`。章节顺序固定，便于跨产品横向对比。
- 一条命令出三份：`python scripts\build_report.py my_report.json --root .` → `<SLUG>.html`（单文件、截图内嵌）+ `<SLUG>.md` + `feishu_doc.md`。数据字段见 `references/report.md`，示例见 `examples/etalien-pc.json`。
- 结构图要**可视**：数据里加 `LANES`（五条泳道）+ `ROWS`（弹窗层/隐藏层），节点会变成可点跳转的链接；不要只放 `pre` 文本树。
- 截图处理：`scripts/make_shots.py`（png → jpg，1000px，质量 84）。

### 6. 校验与收尾

- [ ] `python scripts\verify_report.py <SLUG>.md` 通过（图片、条数、编号、章节）
- [ ] 每个页面都写了：路径、类型、说明、要点、跳转、限制
- [ ] 技术观察有具体数字（体积、端口、驱动、路由表大小）
- [ ] "没做到的部分"写清楚（未支付、未开加速、点了没反应）
- [ ] 客户端退出、系统状态复原、临时文件清理

## 发布到飞书（可选）

`feishu_doc.md` 已经按飞书格式写好图片路径（`@./shots/xxx.jpg`），用 lark-cli 直接灌进目标文档：

```powershell
& $lark docs +fetch  --doc "<文档URL>"                       # 先确认能读、看是否已有内容
& $lark docs +update --doc "<文档URL>" --command overwrite --doc-format markdown --content "@./feishu_doc.md"
& $lark docs +fetch  --doc "<文档URL>" --doc-format markdown  # 回读校验章节与图片
```

写入失败的三种真实原因（按概率排序）：

1. **没有编辑权**：`4030004 No permission to operate on this document`。机器人/账号必须先在协作者名单里（wiki 页面：右上「分享 → 添加协作者」）。
2. **用户 token 过期**：`auth status` 里 `tokenStatus: expired`。用 `auth login --no-wait --json` 走设备码重新授权，再 `auth login --device-code <code>`。
3. **登录态存不下**：`~/.lark-cli` 与 `%LOCALAPPDATA%\lark-cli\keysigner` 必须可写，否则 DPoP key 建不出来（报 `failed to acquire key storage lock`）。沙箱只允许写工作区时，要么给一次更高权限，要么改用机器人身份。
4. Markdown 里的图片会逐张上传，单张 ≤ 20MB；30+ 张图一次写入要留足超时（≥ 5 分钟）。

## 硬规则（血泪版）

1. **Windows 上，客户端以管理员运行时，你的注入会被 UIPI 丢弃。** 表现为：鼠标不动、点击无效、键盘无反应。解决：用 `scripts/win_admin.ps1` 以同等权限跑点击脚本。不要怀疑坐标，先查权限。
2. **`SetCursorPos` 可能失败**（返回 false / 错误 203），但 `mouse_event` 相对移动通常可用。点击一律走"读当前位置 → 相对小步移动 → 闭环收敛 → 按下抬起"。
3. **窗口会被拖走**（无边框窗口的上半部分常是拖拽区）。每次动作前重读 `GetWindowRect`，不要缓存坐标。
4. **PowerShell 5.1 按 ANSI 读 .ps1**。脚本里有中文就会乱码导致匹配失败。所有 `.ps1` 保持纯 ASCII；要中文就写 UTF-8 BOM。
5. **PowerShell 变量不区分大小写**：`$h`（窗口句柄）和 `$H`（窗口高度）是同一个变量，一次赋值就把句柄冲掉了。命名一律 `$winH/$winW/$hwnd`。
6. **提权进程的 stdout 收不到**。`Start-Process -Verb RunAs` 后把输出重定向到文件，再 `Get-Content`。
7. **不要碰钱和账号**：停在扫码页、不发验证码、不点注销、不做真实支付。
8. **不要开危险功能**：准星、外挂类、修复工具（可能改 hosts）、加速（会改路由）——除非调研必需，且用完立刻停。
9. **修复类工具往往没有二次确认**。点了就执行。先截图 hover 态，再决定要不要真点。
10. **外部信息要标来源性质**：官网一手 / 渠道半官方 / 第三方媒体（可能软文）/ 用户传闻。软文不要当结论。
11. **手机截图的预览尺寸 ≠ 物理像素**。`read_image` 给的是缩放图（如 869×1918），`adb input tap` 要物理像素（如 1224×2700）：比例 = `wm size` 的宽 / 预览宽（本例 1.409）。不换算就会"点哪哪不对"，而且看起来像 App 的 bug。
12. **`uiautomator dump` 只对原生 View 有效**。自绘 / Flutter / Unity 页面只返回 1–3 个容器节点，最多加底栏几个 TextView；这种页面只能截图判读，弹层、设置、关于通常是原生，可以 dump 取精确坐标。
13. **`Set-Content -Encoding UTF8` 会写 BOM**，Python `json.load` 直接炸。要么用 ASCII 写 JSON，要么读的时候 `encoding="utf-8-sig"`。另外 `$HOME` 是只读自动变量，参数别叫 `-Home`。
14. **区块只写截图上看得见的**。`absent` 表示「专门找过、确实没有」，不能凭印象写；拿不准就用 `unknown` 并写进 `unverified`。判断类的话放 `points`，不要塞进 `blocks` 的内容栏。

## 文件结构

```
<workspace>/<product>/
  cap.ps1 / win_ctl.ps1        运行期脚本（从 scripts/ 复制）
  L0_home.png ...              原始截图（保留，便于重裁）
  strings.txt                  可选：二进制里抠出的 UI 字符串
  report_data.json             报告内容（结构见 templates/report.json）
  report/
    <产品>_页面层级树与功能清单.md
    <产品>_页面树.html
    feishu_doc.md
    shots/01_xxx.jpg ...
```

## 产出质量基线

- 报告 15k–20k 字符；每个页面 3 条要点起步。
- 结论 4–5 条，必须包含"它靠什么赚钱"和"它真正的竞品是谁"。
- 技术观察 ≥ 8 行，且每行有可核验的数字或路径。
- 风险清单 ≥ 4 条，每条能对应到具体页面或组件。
- **产品判断只写三块**：1. 主要功能（能力面）/ 2. 商业变现（钱从哪来）/ 3. 活动运营（做了什么活动），每块可写 3–5 条。不写「竞品是谁」这类推测。
- 落飞书后必须 `docs +fetch` 回读一次：章节数、图片数、表格是否完整。
