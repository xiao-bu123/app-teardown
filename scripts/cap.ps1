param(
    [string]$Name = "",
    [int]$X = -1,
    [int]$Y = -1,
    [switch]$Back,
    [switch]$List,
    [int]$WaitMs = 1500,
    [string]$OutDir = $PSScriptRoot
)

# Cold-start helper. Windows PowerShell 5.1 has no $PSScriptRoot issue, but the
# $HOME automatic variable is read-only: never name a parameter $Home.
# Call with: powershell.exe -NoProfile -ExecutionPolicy Bypass -File cap.ps1 -Name L0_home

if ($Back) { adb shell input keyevent 4 | Out-Null; Start-Sleep -Milliseconds $WaitMs }
if ($X -ge 0 -and $Y -ge 0) { adb shell input tap $X $Y | Out-Null; Start-Sleep -Milliseconds $WaitMs }

if ($Name -ne "") {
    adb shell screencap -p /sdcard/_dsh_s.png | Out-Null
    adb pull /sdcard/_dsh_s.png (Join-Path $OutDir "$Name.png") 2>$null | Out-Null
    "SHOT: $Name.png"
}

if ($List) {
    adb shell uiautomator dump /sdcard/_dsh_ui.xml 2>$null | Out-Null
    $xml = Join-Path $OutDir "_ui.xml"
    adb pull /sdcard/_dsh_ui.xml $xml 2>$null | Out-Null
    if (Test-Path $xml) {
        [xml]$x = Get-Content $xml -Encoding UTF8
        $i = 0
        foreach ($n in $x.SelectNodes("//node")) {
            $t = "$($n.text)"; $d = "$($n.'content-desc')"
            if ([string]::IsNullOrWhiteSpace($t) -and [string]::IsNullOrWhiteSpace($d) -and "$($n.clickable)" -ne "true") { continue }
            if ($n.bounds -match '\[(\d+),(\d+)\]\[(\d+),(\d+)\]') {
                $cx = [int](([int]$matches[1] + [int]$matches[3]) / 2)
                $cy = [int](([int]$matches[2] + [int]$matches[4]) / 2)
                $i++
                "{0,3}. {1,-16} clk={2} ({3},{4}) t='{5}' d='{6}'" -f $i, (($n.class -split '\.')[-1]), $n.clickable, $cx, $cy, $t, $d
            }
        }
    }
}
