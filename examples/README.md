# 示例：外星仔加速器 PC 版

`etalien-pc.json` 是一份**真实项目的完整数据文件**（17 个页面、5 条泳道、5 张表），用来抄结构，不是拿来直接出图的。

## 怎么用

```powershell
# 1. 复制成你的数据文件，改内容
Copy-Item etalien-pc.json ..\..\my_app.json

# 2. 截图：png → jpg（1000px）
python ..\scripts\make_shots.py <png目录> .\shots

# 3. 一条命令出五份：桌面 HTML / 手机 HTML / MD / 单文件 MD / 飞书 MD
python ..\scripts\build_report.py my_app.json --root .

# 4. 自检
python ..\scripts\verify_report.py my_app.md
```

## 注意

- JSON 里的 `img` **不带 `.jpg`**（渲染时补），本目录**不含截图**，直接跑会报 FileNotFoundError。先把截图放进 `shots/`，或把 `img` 置空。
- 顶层字段是大写（`SLUG/TITLE/META/...`）；`SECTIONS[].num` 是 `"1"`、`"2"`。
- `LANES`/`ROWS`/`TABS` 是可选的，去掉就不生成结构图。
- 节点 `kind` 只能是 `func`、`content`、`pay`、`sys`，对应紫/绿/橙/蓝。
- `CLEAN` 第一行是表头，后面每行是一行功能。

## 参考

- 字段全表：`../references/report.md`
- 写作要求（结论/页面描述怎么写得不像废话）：`../references/writing.md`
- 同项目成品：`E:\dswork\wxz_pc\report\`
