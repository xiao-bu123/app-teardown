# 踩坑清单（按踩到的顺序）

## 1. 输入全部被丢弃（最贵的一课）

**现象**：窗口能截到、`GetForegroundWindow` 也对，但点击/键盘毫无反应，截图前后完全一致。
**原因**：客户端以管理员（High 完整性）运行；我们的进程是 Medium（甚至 Low，AppContainer），UIPI 会把跨完整性级别的注入直接丢掉，`SendInput` 仍返回成功。
**识别**：

```powershell
whoami /groups | Select-String 'S-1-16-'       # Medium / Low
Stop-Process -Id <客户端的pid>                   # Access denied => 对方更高
```

**解决**：用 `scripts/win_admin.ps1` 以同权限跑 `win_ctl.ps1`。UAC 若是"管理员账户：不提示直接提升"，不会弹窗。

## 2. `SetCursorPos` 失败但 `mouse_event` 相对移动可用

**现象**：`SetCursorPos(500,500)` 返回 False、`GetLastError=203`，光标纹丝不动；但 `mouse_event(MOVE, dx, dy)` 能动。
**解决**：闭环相对移动（读位置 → 小步走 → 收敛到 ±2px）。不要写成"一步到位"，鼠标加速会放大误差。

## 3. PowerShell 变量大小写不敏感

```powershell
$h = [Win32]::FindWindow(...)   # 句柄
$H = $r.Bottom - $r.Top         # 同一变量！
```
结果：后面的 `GetWindowRect($h)` 收到的是高度 648，返回 0×0。命名改成 `$hwnd/$winH/$winW`。

## 4. .ps1 中文导致匹配失败

PowerShell 5.1 默认按 ANSI(GBK) 读无 BOM 的脚本。文件里写中文标题去 `FindWindow('外星仔加速器')`，实际拿到乱码，永远找不到窗口。
**解决**：脚本只写 ASCII；必须中文就存成 **UTF-8 with BOM**（`New-Object System.Text.UTF8Encoding($true)`）。

## 5. 窗口自己会跑

无边框 Flutter 窗口的顶部整条是拖拽区。点 tab 时若光标有微小位移，会被当成拖动，窗口位置从 (658,158) 变成 (-96,104)。
**解决**：每次动作前重读 `GetWindowRect`；截图和点击都用"当前 rect + 相对坐标"。

## 6. 截图截到了别的窗口

`CopyFromScreen` 截屏幕，不截窗口。工具链跑完一轮后，DSH/浏览器会抢前台，再截就是别人。
**解决**：`SetForegroundWindow` + `BringWindowToTop`，等 300ms 再截；必要时校验截图像素（不含对方的白色背景）。

## 7. 提权进程的输出收不到

`Start-Process -Verb RunAs` 起的进程不在当前控制台。`Write-Output` 全丢。
**解决**：`... *> 'last.log'`，`-Wait` 后 `Get-Content`。

## 8. 找不到进程 / 看不到窗口标题

低完整性进程只能枚举同级进程；`Get-Process` 里没有目标，`MainWindowTitle` 全是空。
**解决**：提权后再枚举；或用 `EnumWindows` + `GetWindowThreadProcessId` 按 pid 找。

## 9. Win11 记事本没有 MainWindowHandle

Store 版记事本是 UWP 壳，`MainWindowHandle = 0`。
**解决**：用类名 `Notepad` / `ApplicationFrameWindow` 枚举，别依赖 `MainWindowHandle`。

## 10. 点击"没反应"≠ 点击失败

有些按钮是**真没反馈**：前置条件不满足（未检测到游戏/平台）、异步请求失败但没 toast、按钮被透明层盖住。
**解决**：点完 1 秒、2 秒各截一张；再枚举该进程所有窗口（可能有隐藏的弹窗）；仍无变化就记为缺陷，不要连点 10 次。

## 11. 修复类按钮没有二次确认

"修复 Hosts"点下去直接改 `C:\Windows\System32\drivers\etc\hosts`，没有确认框。
**解决**：先 hover 截图，确认交互；真要执行前备份 hosts，执行后对比 mtime。

## 12. WebView2 页面点不动原生控件

H5 页里 `uiautomator` 只有 WebView 节点；Windows 端 Flutter 的 WebView 也不暴露 UIA 子树。
**解决**：纯坐标点击 + 截图判断；必要时从缓存里挖 URL，直接 `ShellExecute` 打开对应页。

## 13. 外部调研的结论可能是错的

本次外部调研称"PC 端没有时长包、永久免费靠广告"；客户端截图里有 88/240/666/1999 小时四档。
**解决**：一手截图优先；外部信息只作背景，冲突时以实拍为准，并在报告里写明"推翻了哪条传闻"。

## 14. 账户/环境状态污染结论

新账号"上次游玩/累计加速"为空，容易被误读成"功能不存在"。
**解决**：在报告"基本盘"里写明账号状态（新号/老号、有无付费），结论里标注"以新账号为准"。

## 15. 截图里有别人的窗口/隐私

截整屏会带上聊天窗口、文件名、其他账号信息。
**解决**：只截目标窗口；必须整屏时裁掉边缘；报告里避免出现他人姓名/手机号/订单号。
