# Windows 桌面客户端：窗口捕获与点击

> 目标：把「点不到 / 点了没反应 / 截出来是黑的」三种常见失败挡在前面。

## 先用 scripts/win_ctl.ps1 摸清窗口

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\win_ctl.ps1 -Action list
```

输出每个可见顶层窗口的 `hwnd / pid / 进程名 / 标题 / 类名 / 矩形`。
记下目标 `hwnd`，以及它是「有边框」还是「无边框自绘」。

```powershell
.\win_ctl.ps1 -Action capture -Hwnd 123456 -Out .\L0_home.png
.\win_ctl.ps1 -Action click -Hwnd 123456 -X 120 -Y 340      # 相对窗口左上角
```

`-X/-Y` 一律是**相对窗口客户区左上角**的坐标，脚本内部会重读 `GetWindowRect` 再换算成屏幕坐标，
所以你不用关心窗口被拖到哪里。

## 截图

1. 首选 `PrintWindow(hwnd, hdc, 2)`（`PW_RENDERFULLCONTENT`），对大多数 Electron/Qt 有效。
2. 返回全黑时退到 `CopyFromScreen`（屏幕区域截图），前提是窗口在前台且未被遮挡。
3. 高 DPI 机器上先 `SetProcessDPIAware()`，否则拿到的矩形是逻辑像素，截图会小一圈。

## 点击

- 顺序：`SetForegroundWindow` → 读 rect → 目标相对坐标 → `SetCursorPos` 绝对定位 →
  `mouse_event` 按下/抬起 → **截图确认画面变化**。
- `SetCursorPos` 可能失败（返回 false 或 203），这时用 `mouse_event(MOUSEEVENTF_MOVE, dx, dy)`
  做相对小步移动，读回光标位置逼近目标，再点击。
- 无边框窗口的上半部分常是拖拽区：点击会被解释成拖窗口，表现为「窗口被拉走、界面没反应」。
  发现窗口位移就立刻重读 rect，并把点击点下移到内容区。
- 每次动作前重读窗口矩形，**不要缓存坐标**（窗口会被用户或其他程序移动/改大小）。

## 权限：UIPI 会静默吞掉你的输入

客户端以管理员运行时，普通权限进程发来的 `SendMessage`/`PostMessage` 会被 UIPI 丢弃；
鼠标键盘注入也可能被拦。表现为：脚本无报错，但界面纹丝不动。

判断：`Get-Process <name> | Select-Object Id,Path` 之后看能否 `OpenProcess`；或用任务管理器
看「以管理员身份运行」。解决：用 `scripts/win_admin.ps1` 以同等权限启动你的脚本。

```powershell
.\win_admin.ps1 -Script .\capture.ps1 -OutLog .\admin.log
```

提权进程的 stdout 拿不到，所以脚本自己把日志写文件，`win_admin.ps1` 轮询该文件回显。

## 其它

- 多显示器：坐标是虚拟屏幕坐标，可能为负；换算时用窗口 rect 而不是屏幕原点。
- 客户端内嵌 H5：截图能拿到画面，但控件树没有；交互只能用坐标。
- 登录态通常在 `%APPDATA%\<产品>` 或 `%LOCALAPPDATA%\<产品>`；先确认是否已登录，再决定能不能看到内页。
- 退出时恢复现场：关闭客户端、停掉它开的服务/驱动、清理临时截图。
