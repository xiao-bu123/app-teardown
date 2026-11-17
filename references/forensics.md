# 静态取证：不用跑起来也能拿到的硬信息

> 目的不是逆向，而是让报告里的「技术观察」有可核验的数字：体积、权限、SDK、签名、端点。

## Android

```powershell
adb shell pm path <pkg>                          # base.apk 路径
adb shell "stat -c %s <apk>"                     # 字节数
adb shell "ls <apk_dir>/lib/"                    # ABI：arm64 / armeabi-v7a
adb shell dumpsys package <pkg> | Select-String "versionName|versionCode|targetSdk|minSdk"
adb shell dumpsys package <pkg> | Select-String -Pattern "requested permissions:" -Context 0,40
```

把 APK 拉回本地后：

```powershell
adb pull <apk> .\<pkg>.apk
& "<sdk>\build-tools\<ver>\aapt.exe" dump badging .\<pkg>.apk     # 包名/版本/权限/启动 Activity
& "<sdk>\build-tools\<ver>\apksigner.bat" verify --print-certs .\<pkg>.apk
```

看权限就能读出产品形态：

- `SYSTEM_ALERT_WINDOW` → 悬浮窗（加速器 HUD、录屏、翻译）
- `QUERY_ALL_PACKAGES` → 枚举已安装应用（游戏加速器、清理类）
- `BIND_VPN_SERVICE` / VpnService → 全局代理
- `TT_PANGOLIN` / `AD_ID` / `com.bytedance` → 穿山甲广告变现
- `FOREGROUND_SERVICE_MEDIA_PROJECTION` → 录屏/投屏

## Windows

```powershell
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*,
                 HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* |
  Where-Object DisplayName -like "*<关键字>*" |
  Select-Object DisplayName,DisplayVersion,Publisher,InstallLocation,InstallDate

Get-AuthenticodeSignature "<exe>" | Format-List Status,SignerCertificate
sc.exe query type= service state= all | Select-String "<关键字>"
```

再补：安装目录体积与文件数、`strings` 抠出的域名/URL、驱动文件（.sys）与其签名、
启动项（Run 键 / 计划任务）。

## Web / 内嵌 H5

- 找入口：客户端里的「用户协议 / 隐私政策 / 帮助中心」几乎都是 H5，URL 就是最好的线索。
- 抓静态资源域名：DevTools Network 或 `strings` 里的 `https://`。
- 前端框架：`window.__INITIAL_STATE__` / `__NUXT__` / `__NEXT_DATA__` 能直接拿到接口返回。

## 写进报告的格式

| 维度 | 结论（带数字/路径） |
|---|---|
| 安装包 | 包名 · 版本 · ABI · 体积 |
| 网络内核 | 用了什么（VpnService / 驱动 / 代理） |
| 权限组合 | 关键权限 + 它对应哪个功能 |
| 第三方 SDK | 广告、统计、推送、登录 |
| 界面栈 | 原生 / 自绘 / 混合，以及依据 |

每条都要能被别人复核：给出命令或路径，而不是「看起来像」。
