# Android：adb 逐页抓取手册

> 这一页是实操细节，踩过的坑都在最后。先读「三分钟开工」，再按「逐页流程」走。

## 三分钟开工

```powershell
adb devices -l                     # 必须出现 "device"，不是 "unauthorized"/空
adb shell getprop ro.product.model
adb shell getprop ro.build.version.release
adb shell getprop ro.build.version.sdk
adb shell wm size                  # 物理分辨率，所有 tap 坐标都用这个尺度
adb shell wm density
adb shell pm list packages | Select-String -Pattern "<关键字>"
adb shell dumpsys package <pkg> | Select-String "versionName|versionCode|targetSdk"
adb shell monkey -p <pkg> -c android.intent.category.LAUNCHER 1
```

`adb devices` 为空时**先查物理连接**，不要急着开模拟器：

```powershell
pnputil /enum-devices /connected | Select-String -Pattern "ADB|Android|MTP|339B|12D1"
```

只看到 `WPD`（MTP/文件传输）而没有 `Android ADB Interface`，说明手机「USB 调试」没开——
直接让用户去开发者选项打开，比折腾模拟器快 100 倍。Honor/Huawei：设置 → 系统和更新 →
开发人员选项 → USB 调试；小米：设置 → 更多设置 → 开发者选项 → USB 调试（并允许 USB 安装）。

## 截图与控件树

```powershell
adb shell screencap -p /sdcard/_s.png
adb pull /sdcard/_s.png .\L0_home.png
adb shell uiautomator dump /sdcard/_u.xml
adb pull /sdcard/_u.xml .\_ui.xml
```

解析（PowerShell 5.1）：

```powershell
[xml]$x = Get-Content .\_ui.xml -Encoding UTF8
$x.SelectNodes("//node") | Where-Object { $_.text -or $_.'content-desc' } |
  ForEach-Object { "{0,-22} {1} clk={2}" -f $_.text, $_.bounds, $_.clickable }
```

`bounds` 形如 `[85,2424][396,2554]`，中心点 `(240, 2489)` 就是要 tap 的坐标。

## 逐页流程（深度优先，上限三级）

1. `monkey` 冷启动 → **L0 首页**截图，列出所有可见入口。
2. 底部 Tab 逐个点，每个截一张（`L0_tab_<名称>`）。
3. 每个 Tab 内点 1–2 个代表性子项（`L1_<tab>_<入口>`）。
4. 弹窗/浮层单独算一页：区服选择、权限请求、付费墙、兑换码、限时优惠。
5. 设置类页面逐项截图，重点拿：版本号、主体、ICP、加速模式、权限相关开关。
6. 商业化页面（会员/充值/去广告/邀请）只浏览**不支付**。
7. 支持页面（FAQ/客服/教程/上架申请）往往是产品自我暴露最多的地方，别漏。
8. 每进一个新页面记录：**页面名 / 承载功能 / 内容类型**，以及**入口名 / 返回路径**。

## 坐标系：最容易翻车的一处

`read_image` 返回的是**缩放后的预览图**（例如 869×1918），而 `adb shell input tap` 用的是
**物理像素**（例如 1224×2700）。比例 = 物理宽 / 预览宽。

> 本次实测：1224 / 869 = **1.409**。不换算的后果是「点哪哪不对」——点分类点到了 Banner，
> 点 Banner 点到了列表，排查半小时才发现是缩放。

做法：先 `adb shell wm size` 拿到物理宽，再除以你看到的预览宽，之后所有坐标乘这个系数；
第一次点击后用截图确认目标是否真的被选中，再继续。

## 什么页面能 dump，什么只能看图

| 壳类型 | 表现 | 应对 |
|---|---|---|
| 原生 View | 节点完整，text/bounds 可读 | 用 dump 精确取坐标 |
| 自绘 / Flutter / Unity | 整页只有 1 个容器，最多底栏几个 TextView | 截图判读 + 按比例换算坐标 |
| 混合（常见） | 主界面自绘，弹层/设置/关于是原生 | 弹层用 dump，主界面用眼睛 |

先 dump 一次：节点数 < 10 且没有业务文本，就当自绘处理，别在 dump 上耗时间。

## 其它硬规则

- `input text` 只吃 ASCII。中文搜索词要么用剪贴板方案，要么换英文关键词。
- `keyevent 4` 是返回，但**部分页面禁用返回**（充值页、部分 H5）；退回靠点 Tab。
- 系统权限弹窗（VPN/通知/位置）先截图再决定：调研类一律优先拒绝；VPN 类可接受，
  **验证完立刻停止**，别让手机带着别人的隧道跑。
- 支付页停在收银台；下载类广告点关闭，别真装第三方 App。
- 别对着一个「点了没反应」的按钮反复点——先记录为缺陷，换个入口再试。

## 环境坑（Windows + PowerShell 5.1）

1. 没有 `pwsh`，只有 `powershell.exe`；执行策略会拦脚本 →
   `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\cap.ps1 -Name L0_home`。
2. `$HOME` 是只读自动变量，参数别起名 `-Home`，否则 `VariableNotWritable`。
3. 包一层脚本调 adb 偶尔**进程不退出**（命令已跑完但挂住）→ 直接逐条执行 adb 命令更稳，
   或用 `Start-Process` 起独立进程。
4. `Set-Content -Encoding UTF8` 写出的 JSON **带 BOM**，Python 读会炸 →
   `json.load(open(p, encoding="utf-8-sig"))`。
5. 中文脚本被按 ANSI 读取会乱码：`.ps1` 尽量纯 ASCII，必须中文就存 UTF-8 BOM。

## 命名与归档

```
<workspace>\<产品>\
  L0_home.png
  L1_tab_mine.png
  L2_settings.png
  L3_accel_hud.png
  shots\01_home.jpg ...      # make_shots.py 生成
  _ui.xml
```

层级前缀 `L0_/L1_/L2_/L3_`，中间是模块，最后是页面；顺序即报告索引顺序。
