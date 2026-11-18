param(
  [string]$action = "shot",
  [string]$serial = "",
  [string]$path = "shot.png",
  [string]$text = "",
  [int]$x = 0,
  [int]$y = 0,
  [int]$x2 = 0,
  [int]$y2 = 0,
  [int]$ms = 300,
  [string]$pkg = ""
)
$adb = "adb"
if (-not (Get-Command adb -ErrorAction SilentlyContinue)) {
  $cand = @("$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe",
            "C:\Android\platform-tools\adb.exe",
            "$env:ProgramFiles\Android\platform-tools\adb.exe")
  foreach ($c in $cand) { if (Test-Path $c) { $adb = $c; break } }
}
$scoped = @()
if ($serial -ne "") { $scoped = @("-s", $serial) }

switch ($action) {
  "devices" { & $adb devices -l }
  "packages" {
    if ($pkg -eq "") { & $adb @scoped shell pm list packages -3 }
    else { & $adb @scoped shell pm list packages | Select-String $pkg }
  }
  "start" {
    if ($pkg -eq "") { Write-Error "need -pkg"; exit 1 }
    & $adb @scoped shell am force-stop $pkg
    & $adb @scoped shell monkey -p $pkg -c android.intent.category.LAUNCHER 1
  }
  "stop" { if ($pkg -ne "") { & $adb @scoped shell am force-stop $pkg } }
  "shot" {
    $dir = Split-Path -Parent $path
    if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }
    $b64 = & $adb @scoped exec-out screencap -p
    # exec-out returns raw bytes in PowerShell 7+; fall back to pull for 5.1
    if ($b64 -is [byte[]]) { [IO.File]::WriteAllBytes($path, $b64) }
    else {
      & $adb @scoped shell screencap -p /sdcard/_shot.png
      & $adb @scoped pull /sdcard/_shot.png $path | Out-Null
      & $adb @scoped shell rm /sdcard/_shot.png
    }
    Write-Output ("SAVED {0} {1} KB" -f $path, [math]::Round((Get-Item $path).Length / 1KB, 1))
  }
  "dump" {
    & $adb @scoped shell uiautomator dump /sdcard/_ui.xml | Out-Null
    & $adb @scoped pull /sdcard/_ui.xml $path | Out-Null
    Write-Output ("DUMPED {0}" -f $path)
  }
  "tap" { & $adb @scoped shell input tap $x $y; Write-Output ("TAP {0},{1}" -f $x, $y) }
  "swipe" { & $adb @scoped shell input swipe $x $y $x2 $y2 $ms; Write-Output ("SWIPE {0},{1} -> {2},{3}" -f $x,$y,$x2,$y2) }
  "text" { & $adb @scoped shell input text $text; Write-Output ("TEXT {0}" -f $text) }
  "back" { & $adb @scoped shell input keyevent 4 }
  "home" { & $adb @scoped shell input keyevent 3 }
  default { Write-Output "actions: devices|packages|start|stop|shot|dump|tap|swipe|text|back|home" }
}
